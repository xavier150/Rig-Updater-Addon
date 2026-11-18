# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: SPDX:MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

import importlib

import bpy

from .. import rua_action
from .. import rua_armature
from .. import rua_check
from . import rua_ui_utils

if "rua_ui_utils" in locals():
    importlib.reload(rua_ui_utils)


class RUA_PT_MainPanel(bpy.types.Panel):
    bl_idname = "RUA_PT_main_panel"
    bl_label = "Rig Updater"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rig Updater'

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        if layout is not None:
            rua_armature.rua_armature_ui.rua_armature_ui_utils.draw(layout, context)
            rua_action.rua_action_ui.rua_action_ui_utils.draw(layout, context)
            rua_check.rua_check_ui.rua_check_ui_utils.draw(layout, context)


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
    RUA_PT_MainPanel,
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
