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
    accordion = bbpl.blender_layout.layout_accordion.get_accordion(context.scene, "rua_actions_accordion")
    if accordion:
        _, panel = accordion.draw(layout)
        if panel:
            panel.operator("rua.update_rig_backward_compatibility")
            panel.operator("rua.update_mesh_skin_weight_backward_compatibility")
