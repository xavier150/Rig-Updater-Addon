# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

import math
from typing import Dict, Optional, Tuple

import bpy

from .. import bbpl, rua_json_utils
from . import rua_scene_props
from . import rua_scene_type
from .rua_scene_lib import rua_scene_lib_utils
from .rua_scene_lib.methods import methods_utils


def load_scene_rules_backward_compatibility(filepath: str) -> rua_scene_type.SceneRulesBackwardCompatibility:
    document = rua_json_utils.require_dict(
        rua_json_utils.load_document(filepath), "JSON", {"scene_rescale_rules", "libraries_update_rules"},
    )
    scale_value = document["scene_rescale_rules"]
    scale_keys = {
        "target_unit_scale", "scale_object_position", "scale_animation_location_channels",
        "scale_rig", "scale_user_view",
    }
    if isinstance(scale_value, dict) and "scale_constraints" in scale_value:
        scale_keys.add("scale_constraints")
    scale_rules = rua_json_utils.require_dict(document["scene_rescale_rules"], "scene_rescale_rules", scale_keys)
    scale = scale_rules["target_unit_scale"]
    scale_property = bpy.types.UnitSettings.bl_rna.properties["scale_length"]
    if (
        isinstance(scale, bool) or not isinstance(scale, (int, float))
        or not math.isfinite(scale) or not scale_property.hard_min <= scale <= scale_property.hard_max # type: ignore
    ):
        raise ValueError(
            f"scene_rescale_rules.target_unit_scale: expected a finite number between "
            f"{scale_property.hard_min} and {scale_property.hard_max}." # type: ignore
        )
    scale_options: Dict[str, bool] = {}
    for name in (
        "scale_object_position", "scale_animation_location_channels", "scale_rig",
        "scale_user_view", "scale_constraints",
    ):
        value = scale_rules.get(name, True) if name == "scale_constraints" else scale_rules[name]
        if not isinstance(value, bool):
            raise ValueError(f"scene_rescale_rules.{name}: expected a boolean.")
        scale_options[name] = value
    tasks = rua_scene_lib_utils.parse_libraries_update_rules(document["libraries_update_rules"])
    return rua_scene_type.SceneRulesBackwardCompatibility(
        rua_scene_type.SceneRescaleRules(
            float(scale), scale_options["scale_object_position"],
            scale_options["scale_animation_location_channels"], scale_options["scale_rig"],
            scale_options["scale_user_view"], scale_options["scale_constraints"],
        ), tasks,
    )


def load_scene_configuration(
    scene: bpy.types.Scene,
) -> Tuple[Optional[rua_scene_type.SceneRulesBackwardCompatibility], Optional[str]]:
    filepath = rua_scene_props.get_scene_rules_filepath(scene)
    error = rua_json_utils.get_config_file_error(filepath)
    if error is not None:
        return None, error
    return load_scene_rules_backward_compatibility(filepath), None


def update_scene_scale(scene: bpy.types.Scene, configuration: rua_scene_type.SceneRulesBackwardCompatibility) -> None:
    unit_settings = scene.unit_settings
    if unit_settings is None:
        raise RuntimeError("Scene unit settings are unavailable.")
    rules = configuration.scene_rescale_rules
    scale_factor = unit_settings.scale_length / rules.target_unit_scale
    # Blender stores the unit scale as a single-precision float.
    if not math.isclose(scale_factor, 1.0, rel_tol=1e-7):
        objects = list(scene.objects)
        root_objects = [
            obj for obj in objects if obj.library is None and obj.parent is None
        ]
        if rules.scale_object_position and root_objects:
            bbpl.scene.scale_utils.scale_objects(
                scale_factor, use_location=True, use_scale=True,
                white_list=root_objects, scene_only=False,
            )
        if rules.scale_animation_location_channels:
            linked_actions = [action for action in bpy.data.actions if action.library is not None]
            bbpl.scene.scale_utils.scale_animations(scale_factor, black_list=linked_actions)
        if rules.scale_rig and objects:
            bbpl.scene.scale_utils.scale_rigs_data(
                scale_factor, white_list=objects, scene_only=True,
            )
        if rules.scale_constraints:
            for obj in objects:
                if obj.library is not None:
                    continue
                constraints = list(obj.constraints)
                if obj.pose is not None:
                    constraints.extend(
                        constraint for bone in obj.pose.bones for constraint in bone.constraints
                    )
                for constraint in constraints:
                    if (
                        isinstance(constraint, bpy.types.ChildOfConstraint)
                        and methods_utils.is_local_constraint(constraint)
                    ):
                        matrix = constraint.inverse_matrix.copy()
                        matrix.translation *= scale_factor
                        constraint.inverse_matrix = matrix
        if rules.scale_user_view:
            bbpl.scene.scale_utils.scale_user_view(scale_factor)
    unit_settings.scale_length = rules.target_unit_scale
