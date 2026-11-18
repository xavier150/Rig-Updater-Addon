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

from ... import rua_skin
from .. import rua_action


class RUA_OT_UpdateRigBackwardCompatibility(bpy.types.Operator):
    bl_idname = "rua.update_rig_backward_compatibility"
    bl_label = "Update Rig Backward Compatibility"
    bl_description = "Update local animation actions for the newer rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> "set[rna_enums.OperatorReturnItems]":
        try:
            rua_action.update_action_backward_compatibility()
        except (RuntimeError, ValueError, AttributeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


class RUA_OT_UpdateMeshSkinWeightBackwardCompatibility(bpy.types.Operator):
    bl_idname = "rua.update_mesh_skin_weight_backward_compatibility"
    bl_label = "Update Mesh Skin Weight Backward Compatibility"
    bl_description = "Update vertex groups on selected meshes for the newer rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> "set[rna_enums.OperatorReturnItems]":
        try:
            rua_skin.rua_skin_utils.update_mesh_skin_weight_backward_compatibility(select_only=True)
        except (RuntimeError, ValueError, AttributeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
    RUA_OT_UpdateRigBackwardCompatibility,
    RUA_OT_UpdateMeshSkinWeightBackwardCompatibility,
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
