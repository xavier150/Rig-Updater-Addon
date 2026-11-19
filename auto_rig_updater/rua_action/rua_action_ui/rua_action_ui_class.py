# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

from typing import TYPE_CHECKING

import bpy

if TYPE_CHECKING:
    import bpy.stub_internal.rna_enums as rna_enums

from ... import bpl
from ... import rua_armature
from ... import rua_json_utils
from ... import rua_rig
from .. import rua_action_utils


class RUA_OT_UpdateRigBackwardCompatibility(bpy.types.Operator):
    bl_idname = "rua.update_rig_backward_compatibility"
    bl_label = "Update Rig Backward Compatibility"
    bl_description = "Update local animation actions for the newer rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> "set[rna_enums.OperatorReturnItems]":
        obj = context.object
        if obj is None or not isinstance(obj.data, bpy.types.Armature):
            self.report({'WARNING'}, "Select an armature to configure the animation migration.")
            return {'CANCELLED'}
        filepath = rua_armature.rua_armature_utils.get_config_filepath(
            obj,
            rua_armature.rua_armature_props.get_object_armature_rig_controllers_backward_compatibility(obj),
        )
        error = rua_json_utils.get_config_file_error(filepath)
        if error is not None:
            print(bpl.color_set.yellow(f"[Rig Updater] Warning: {error}"))
            self.report({'WARNING'}, error)
            return {'CANCELLED'}
        configuration = rua_rig.rua_rig_utils.load_rig_controllers_backward_compatibility(filepath)
        rua_action_utils.update_action_backward_compatibility(configuration)
        return {'FINISHED'}


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
    RUA_OT_UpdateRigBackwardCompatibility,
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
