# SPDX-FileCopyrightText: 2019-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

from typing import Iterable, List, NamedTuple, Optional, Sequence, Tuple, cast

import bpy

from .. import bbpl
from .. import rua_armature
from .. import rua_json_utils
from .. import rua_rig


class InvalidActionChannel(NamedTuple):
    action: str
    slot: str
    data_path: str
    array_index: int


def load_armature_configuration(
    armature: bpy.types.Object,
) -> Tuple[Optional[rua_rig.rua_rig_type.RigControllersBackwardCompatibility], Optional[str]]:
    filepath = rua_armature.rua_armature_utils.get_config_filepath(
        armature, rua_armature.rua_armature_props.get_object_armature_rig_controllers_backward_compatibility(armature),
        property_name="rua_armature_rig_controllers_backward_compatibility",
    )
    error = rua_json_utils.get_config_file_error(filepath)
    if error is not None:
        return None, error
    return rua_rig.rua_rig_utils.load_rig_controllers_backward_compatibility(filepath), None


def get_actions_for_search(armature: Optional[bpy.types.Object], action_search: str) -> List[bpy.types.Action]:
    if action_search == "all_actions":
        actions = list(bpy.data.actions)
    else:
        if armature is None or not isinstance(armature.data, bpy.types.Armature):
            raise ValueError(f"An armature is required for action search '{action_search}'.")
        if action_search == "used_actions":
            actions = bbpl.action.action_utils.get_used_actions(armature)
        elif action_search == "revelant_actions":
            actions = bbpl.action.action_utils.get_relevant_actions([armature])
        elif action_search == "revelant_and_used_actions":
            actions = bbpl.action.action_utils.get_relevant_actions([armature])
            for action in bbpl.action.action_utils.get_used_actions(armature):
                if action not in actions:
                    actions.append(action)
        else:
            raise ValueError(f"Unknown action search: {action_search!r}.")
    return [action for action in actions if action.library is None]


def get_configured_actions(
    armature: bpy.types.Object, configuration: rua_rig.rua_rig_type.RigControllersBackwardCompatibility,
) -> List[bpy.types.Action]:
    actions: List[bpy.types.Action] = []
    for task in configuration.update_tasks:
        for action in get_actions_for_search(armature, task.action_search):
            if action not in actions:
                actions.append(action)
    return actions


def _rna_array_size(prop: bpy.types.bpy_prop_array) -> int:
    items = cast(Sequence[object], prop)
    size = len(items)
    if size and isinstance(items[0], bpy.types.bpy_prop_array):
        return size * _rna_array_size(items[0])
    return size


def find_invalid_action_channels(
    armature: bpy.types.Object, actions: List[bpy.types.Action],
) -> Tuple[List[InvalidActionChannel], List[Tuple[str, str, str]]]:
    if not isinstance(armature.data, bpy.types.Armature):
        raise ValueError(f"Object '{armature.name}' is not an armature.")
    invalid: List[InvalidActionChannel] = []
    skipped: List[Tuple[str, str, str]] = []

    def check_curve(action: bpy.types.Action, slot_name: str, target: bpy.types.ID, curve: bpy.types.FCurve) -> None:
        try:
            prop = target.path_resolve(curve.data_path, False)
        except ValueError:
            invalid.append(InvalidActionChannel(action.name, slot_name, curve.data_path, curve.array_index))
            return
        if not isinstance(prop, bpy.types.bpy_prop):
            invalid.append(InvalidActionChannel(action.name, slot_name, curve.data_path, curve.array_index))
        elif isinstance(prop, bpy.types.bpy_prop_array):
            if curve.array_index >= _rna_array_size(prop):
                invalid.append(InvalidActionChannel(action.name, slot_name, curve.data_path, curve.array_index))
        elif curve.array_index != 0:
            invalid.append(InvalidActionChannel(action.name, slot_name, curve.data_path, curve.array_index))

    for action in actions:
        if bpy.app.version >= (4, 4, 0):
            for slot in action.slots:
                if slot.target_id_type == 'OBJECT':
                    target = armature
                elif slot.target_id_type == 'ARMATURE':
                    target = armature.data
                else:
                    skipped.append((action.name, slot.name_display, slot.target_id_type))
                    continue
                for layer in action.layers:
                    for strip in layer.strips:
                        if strip.type == 'KEYFRAME':
                            channelbag = strip.channelbag(slot)
                            if channelbag is not None:
                                for curve in channelbag.fcurves:
                                    check_curve(action, slot.name_display, target, curve)
        else:
            for curve in cast(Iterable[bpy.types.FCurve], getattr(action, "fcurves")):
                check_curve(action, "Legacy Slot", armature, curve)
    return invalid, skipped


def _controller_data_path(name: str) -> str:
    return f'pose.bones["{bpy.utils.escape_identifier(name)}"]'


def update_action_backward_compatibility(
    configuration: rua_rig.rua_rig_type.RigControllersBackwardCompatibility,
    print_log: bool = False,
    *,
    armature: Optional[bpy.types.Object] = None,
) -> None:
    rig_updater = bbpl.backward_compatibility.rig_action_updater.RigActionUpdater()
    rig_updater.print_log = print_log

    task_actions = [
        (task, get_actions_for_search(armature, task.action_search))
        for task in configuration.update_tasks
    ]
    print("Starting action update backward compatibility...")

    for task, actions in task_actions:
        deform_bone_paths: List[str] = []
        if any(isinstance(section, rua_rig.rua_rig_type.RemoveDeformBonesSection) for section in task.sections):
            if armature is None or not isinstance(armature.data, bpy.types.Armature):
                raise ValueError("An armature is required to remove deform-bone action channels.")
            deform_bone_paths = [
                _controller_data_path(bone.name)
                for bone in armature.data.bones if bone.use_deform
            ]
        for action in actions:
            if action.library:
                continue
            print(f"Updating action: {action.name}")
            for section in task.sections:
                if isinstance(section, rua_rig.rua_rig_type.RemoveStartingChannelSection):
                    rig_updater.remove_action_curve_by_data_path(action, section.prefixes, starts_with=True)
                    continue
                if isinstance(section, rua_rig.rua_rig_type.RemoveDeformBonesSection):
                    rig_updater.remove_action_curve_by_data_path(action, deform_bone_paths)
                    continue
                is_channel = section.target == "channel"
                for operation in section.operations:
                    old_paths = operation.old if is_channel else [_controller_data_path(name) for name in operation.old]
                    if isinstance(operation, rua_rig.rua_rig_type.RigControllerReplaceOperation):
                        new_path = operation.new if is_channel else _controller_data_path(operation.new)
                        group_name_replacements = None
                        if not is_channel:
                            group_name_replacements = {
                                _controller_data_path(old_name): (old_name, operation.new)
                                for old_name in operation.old
                            }
                        rig_updater.update_action_curve_data_path(
                            action, old_paths, new_path,
                            conflit_resolution=operation.conflit_resolution, exact_match=is_channel,
                            group_name_replacements=group_name_replacements,
                        )
                    else:
                        rig_updater.remove_action_curve_by_data_path(action, old_paths, exact_match=is_channel)

    rig_updater.print_update_log()
