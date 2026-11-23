# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

import bpy

from ... import bbpl


def draw(layout: bpy.types.UILayout, context: bpy.types.Context) -> None:
    rig_accordion = bbpl.blender_layout.layout_accordion.get_accordion(context.scene, "rua_rig_actions_accordion")
    if rig_accordion:
        _, panel = rig_accordion.draw(layout)
        if panel:
            panel.operator("rua.update_armature_deform_bones")
            row = panel.row(align=True)
            row.operator("rua.update_meshes_weights_backward_compatibility")
            row.operator("rua.update_meshes_weights_backward_compatibility_select_only")

    scene_accordion = bbpl.blender_layout.layout_accordion.get_accordion(context.scene, "rua_scene_action_accordion")
    if scene_accordion:
        _, panel = scene_accordion.draw(layout)
        if panel:
            panel.operator("rua.update_scene_libraries")
            panel.operator("rua.update_scene_scale")
            row = panel.row(align=True)
            row.operator("rua.update_actions_backward_compatibility")
            row.operator("rua.update_actions_backward_compatibility_all")
