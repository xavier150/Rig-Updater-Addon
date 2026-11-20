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
    accordion = bbpl.blender_layout.layout_accordion.get_accordion(context.scene, "rua_config_accordion")
    if accordion:
        _, panel = accordion.draw(layout)
        if panel:
            panel.prop(context.scene, "rua_scene_rules_backward_compatibility")
            obj = context.object
            if obj is None or not isinstance(obj.data, bpy.types.Armature):
                panel.label(text="Select an armature to configure its JSON files.")
                return
            panel.prop(obj, "rua_armature_mesh_weight_backward_compatibility")
            panel.prop(obj, "rua_armature_rig_controllers_backward_compatibility")
