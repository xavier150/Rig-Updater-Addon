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
    accordion = bbpl.blender_layout.layout_accordion.get_accordion(context.scene, "rua_checks_accordion")
    if accordion:
        _, panel = accordion.draw(layout)
        if panel:
            row = panel.row(align=True)
            row.operator("rua.check_meshes_weights")
            row.operator("rua.check_meshes_weights_all")
            row = panel.row(align=True)
            row.operator("rua.check_actions")
            row.operator("rua.check_actions_all")
