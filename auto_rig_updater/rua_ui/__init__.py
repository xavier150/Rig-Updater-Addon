# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: SPDX:MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

import importlib

import bpy

from .. import bbpl
from .. import rua_action
from .. import rua_skin
from . import rua_ui_utils

if "rua_ui_utils" in locals():
    importlib.reload(rua_ui_utils)


class RUA_PT_MainPanel(bpy.types.Panel):
    bl_idname = "RUA_PT_main_panel"
    bl_label = "Rig Updater"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rig Updater'

    def draw(self, context):
        accordion = bbpl.blender_layout.layout_accordion.get_accordion(context.scene, "rua_actions_accordion")
        if accordion:
            _, panel = accordion.draw(self.layout)
            if panel:
                panel.operator("rua.update_rig_backward_compatibility")
                panel.operator("rua.update_mesh_skin_weight_backward_compatibility")


class RUA_OT_UpdateRigBackwardCompatibility(bpy.types.Operator):
    bl_idname = "rua.update_rig_backward_compatibility"
    bl_label = "Update Rig Backward Compatibility"
    bl_description = "Update local animation actions for the newer rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
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

    def execute(self, context):
        try:
            rua_skin.update_mesh_skin_weight_backward_compatibility(select_only=True)
        except (RuntimeError, ValueError, AttributeError) as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        return {'FINISHED'}


classes = (
    RUA_OT_UpdateRigBackwardCompatibility,
    RUA_OT_UpdateMeshSkinWeightBackwardCompatibility,
    RUA_PT_MainPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.rua_actions_accordion = bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Actions")


def unregister():
    del bpy.types.Scene.rua_actions_accordion

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
