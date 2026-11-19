# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

from typing import TYPE_CHECKING, List, Set

import bpy

if TYPE_CHECKING:
    import bpy.stub_internal.rna_enums as rna_enums

from ... import bpl
from ... import rua_armature
from .. import rua_action_utils


def _check_armatures(operator: bpy.types.Operator, armatures: List[bpy.types.Object]) -> "Set[rna_enums.OperatorReturnItems]":
    if not armatures:
        message = "No armatures found in the scene."
        print(bpl.color_set.yellow(f"[Rig Updater] Warning: {message}"))
        operator.report({'WARNING'}, message)
        return {'CANCELLED'}
    invalid_count = 0
    skipped_count = 0
    checked_count = 0
    errors = 0
    for armature in armatures:
        configuration, error = rua_action_utils.load_armature_configuration(armature)
        if error is not None:
            print(bpl.color_set.yellow(f'[Rig Updater] Warning: Armature "{armature.name}": {error}'))
            errors += 1
            continue
        if configuration is None:
            raise RuntimeError("Rig configuration loading returned no configuration.")
        actions = rua_action_utils.get_configured_actions(armature, configuration)
        invalid, skipped = rua_action_utils.find_invalid_action_channels(armature, actions)
        checked_count += 1
        print(f'[Rig Updater] Armature "{armature.name}": checked {len(actions)} actions.')
        for channel in invalid:
            print(bpl.color_set.yellow(
                f'Warning: Action "{channel.action}", channel "{channel.data_path}" '
                f'(index {channel.array_index}) not found in slot "{channel.slot}" '
                f'for armature "{armature.name}".'
            ))
        for action_name, slot_name, target_type in skipped:
            print(bpl.color_set.yellow(
                f'Warning: Action "{action_name}", slot "{slot_name}" targets {target_type}, '
                f'not armature "{armature.name}"; skipped.'
            ))
        invalid_count += len(invalid)
        skipped_count += len(skipped)
    if checked_count == 0:
        operator.report({'WARNING'}, "No armatures could be checked. See the system console.")
        return {'CANCELLED'}
    message = (
        f"{invalid_count} invalid channels; {skipped_count} slots skipped; "
        f"{errors} armatures not checked. See the system console."
    )
    operator.report({'WARNING'} if invalid_count or skipped_count or errors else {'INFO'}, message)
    return {'FINISHED'}


class RUA_OT_CheckActionsActive(bpy.types.Operator):
    bl_idname = "rua.check_actions_active"
    bl_label = "Check Action (Active)"
    bl_description = "Check configured actions against the target armature"

    if TYPE_CHECKING:
        target_object: str
    else:
        target_object: bpy.props.StringProperty(
            name="Target Object",
            description="Armature object name; leave empty to use the active armature",
            default="",
            options={'SKIP_SAVE'},
        )

    def execute(self, context: bpy.types.Context) -> "Set[rna_enums.OperatorReturnItems]":
        armature, error = rua_armature.rua_armature_utils.get_target_armature(context, self.target_object)
        if error is not None:
            print(bpl.color_set.yellow(f"[Rig Updater] Warning: {error}"))
            self.report({'WARNING'}, error)
            return {'CANCELLED'}
        if armature is None:
            raise RuntimeError("Target armature resolution returned no object.")
        return _check_armatures(self, [armature])


class RUA_OT_CheckActionsAll(bpy.types.Operator):
    bl_idname = "rua.check_actions_all"
    bl_label = "Check Actions (All)"
    bl_description = "Check configured actions against every armature in the scene"

    def execute(self, context: bpy.types.Context) -> "Set[rna_enums.OperatorReturnItems]":
        if context.scene is None:
            self.report({'WARNING'}, "No active scene.")
            return {'CANCELLED'}
        armatures = [obj for obj in context.scene.objects if isinstance(obj.data, bpy.types.Armature)]
        return _check_armatures(self, armatures)


class RUA_OT_UpdateRigBackwardCompatibility(bpy.types.Operator):
    bl_idname = "rua.update_rig_backward_compatibility"
    bl_label = "Update Rig Backward Compatibility"
    bl_description = "Update local animation actions for the newer rig"
    bl_options = {'REGISTER', 'UNDO'}

    if TYPE_CHECKING:
        target_object: str
    else:
        target_object: bpy.props.StringProperty(
            name="Target Object",
            description="Armature object name; leave empty to use the active armature",
            default="",
            options={'SKIP_SAVE'},
        )

    def execute(self, context: bpy.types.Context) -> "Set[rna_enums.OperatorReturnItems]":
        obj, error = rua_armature.rua_armature_utils.get_target_armature(context, self.target_object)
        if error is not None:
            print(bpl.color_set.yellow(f"[Rig Updater] Warning: {error}"))
            self.report({'WARNING'}, error)
            return {'CANCELLED'}
        if obj is None:
            raise RuntimeError("Target armature resolution returned no object.")
        configuration, error = rua_action_utils.load_armature_configuration(obj)
        if error is not None:
            print(bpl.color_set.yellow(f"[Rig Updater] Warning: {error}"))
            self.report({'WARNING'}, error)
            return {'CANCELLED'}
        if configuration is None:
            raise RuntimeError("Rig configuration loading returned no configuration.")
        rua_action_utils.update_action_backward_compatibility(configuration, armature=obj)
        return {'FINISHED'}


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
    RUA_OT_CheckActionsActive,
    RUA_OT_CheckActionsAll,
    RUA_OT_UpdateRigBackwardCompatibility,
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
