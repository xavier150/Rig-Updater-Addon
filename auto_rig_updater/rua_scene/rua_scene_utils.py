# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

import math
from typing import Optional, Tuple

import bpy

from .. import rua_json_utils
from . import rua_scene_props
from . import rua_scene_type
from .rua_scene_lib import rua_scene_lib_utils


def load_scene_rules_backward_compatibility(filepath: str) -> rua_scene_type.SceneRulesBackwardCompatibility:
    document = rua_json_utils.require_dict(
        rua_json_utils.load_document(filepath), "JSON", {"scene_rescale_rules", "libraries_update_rules"},
    )
    scale_rules = rua_json_utils.require_dict(
        document["scene_rescale_rules"], "scene_rescale_rules", {"target_unit_scale"},
    )
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
    tasks = rua_scene_lib_utils.parse_libraries_update_rules(document["libraries_update_rules"])
    return rua_scene_type.SceneRulesBackwardCompatibility(
        rua_scene_type.SceneRescaleRules(float(scale)), tasks,
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
    if scene.unit_settings:
        scene.unit_settings.scale_length = configuration.scene_rescale_rules.target_unit_scale
