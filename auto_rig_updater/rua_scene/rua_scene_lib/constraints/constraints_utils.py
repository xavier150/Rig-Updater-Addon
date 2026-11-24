# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

from typing import Callable, Dict, Iterable, List, Optional, Tuple, cast

import bpy


def is_local_constraint(constraint: bpy.types.Constraint) -> bool:
    owner = cast(bpy.types.Object, constraint.id_data)
    if cast(Optional[bpy.types.Library], owner.library) is not None or constraint.is_override_data:
        return False
    # Newly created overrides in Blender 3.6 can lack inherited constraint flags.
    if owner.override_library is not None:
        reference = owner.override_library.reference
        if isinstance(reference, bpy.types.Object):
            reference_constraints: List[bpy.types.Constraint] = list(reference.constraints)
            if reference.pose is not None:
                reference_constraints.extend(
                    item for bone in reference.pose.bones for item in bone.constraints
                )
            path = constraint.path_from_id()
            if any(item.path_from_id() == path for item in reference_constraints):
                return False
    return True


def bone_name_mapping(obj: bpy.types.Object) -> List[Tuple[List[str], str]]:
    """Load controller and deform bone replacement operations from the new rig."""
    from ....rua_armature import rua_armature_props, rua_armature_utils
    from ....rua_rig import rua_rig_type, rua_rig_utils
    from ....rua_skin import rua_skin_utils

    mapping: List[Tuple[List[str], str]] = []
    if hasattr(obj, "rua_armature_rig_controllers_backward_compatibility"):
        value = rua_armature_props.get_object_armature_rig_controllers_backward_compatibility(obj)
        if value.strip():
            filepath = rua_armature_utils.get_config_filepath(
                obj, value, property_name="rua_armature_rig_controllers_backward_compatibility",
            )
            configuration = rua_rig_utils.load_rig_controllers_backward_compatibility(filepath)
            mapping.extend(
                (operation.old, operation.new)
                for task in configuration.update_tasks
                for section in task.sections
                if isinstance(section, rua_rig_type.ReplaceSection) and section.target == "bone"
                for operation in section.operations
            )
    if hasattr(obj, "rua_armature_mesh_weight_backward_compatibility"):
        value = rua_armature_props.get_object_armature_mesh_weight_backward_compatibility(obj)
        if value.strip():
            filepath = rua_armature_utils.get_config_filepath(
                obj, value, property_name="rua_armature_mesh_weight_backward_compatibility",
            )
            deform_configuration = rua_skin_utils.load_mesh_weight_backward_compatibility(filepath)
            mapping.extend(
                (operation.old, operation.new)
                for task in deform_configuration.update_tasks
                for operation in task.replace_operations
            )
    return mapping


def new_bone_name(name: str, mapping: List[Tuple[List[str], str]]) -> str:
    for old_names, new_name in mapping:
        if name in old_names:
            name = new_name
    return name


def local_constraint_names(
    source: bpy.types.Object, include_bones: bool,
) -> Tuple[List[str], Dict[str, List[str]]]:
    object_names = [constraint.name for constraint in source.constraints if is_local_constraint(constraint)]
    bone_names = {
        bone.name: [constraint.name for constraint in bone.constraints if is_local_constraint(constraint)]
        for bone in source.pose.bones
    } if source.pose is not None and include_bones else {}
    return object_names, {name: names for name, names in bone_names.items() if names}


def copy_scene_constraints(
    source: bpy.types.Object, destination: bpy.types.Object,
    object_names: List[str], bone_names: Dict[str, List[str]],
) -> None:
    """Restore local constraints, skipping bones absent from the new rig."""
    for name in object_names:
        destination.constraints.copy(source.constraints[name])
    if source.pose is None or destination.pose is None:
        return
    mapping = bone_name_mapping(destination)
    for bone_name, names in bone_names.items():
        destination_bone = destination.pose.bones.get(new_bone_name(bone_name, mapping))
        if destination_bone is not None:
            for name in names:
                destination_bone.constraints.copy(source.pose.bones[bone_name].constraints[name])


def capture_references(
    constraints: Iterable[bpy.types.Constraint], capture: Callable[[object, str], None],
) -> None:
    for constraint in constraints:
        capture(constraint, "target")
        capture(constraint, "space_object")
        if isinstance(constraint, bpy.types.ArmatureConstraint):
            for item in constraint.targets:
                capture(item, "target")


def remap_subtarget(
    owner: object, target: bpy.types.Object,
    mappings: Dict[bpy.types.Object, List[Tuple[List[str], str]]],
) -> None:
    subtarget: object = getattr(owner, "subtarget", None)
    if isinstance(subtarget, str) and target.type == 'ARMATURE':
        if target not in mappings:
            mappings[target] = bone_name_mapping(target)
        setattr(owner, "subtarget", new_bone_name(subtarget, mappings[target]))
