# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

import importlib

import bpy

from ... import bbpl
from . import rua_check_ui_class
from . import rua_check_ui_utils

if "rua_check_ui_class" in locals():
    importlib.reload(rua_check_ui_class)
if "rua_check_ui_utils" in locals():
    importlib.reload(rua_check_ui_utils)


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)

    rua_check_ui_class.register()
    setattr(
        bpy.types.Scene,
        "rua_checks_accordion",
        bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Checks"),
    )


def unregister() -> None:
    delattr(bpy.types.Scene, "rua_checks_accordion")
    rua_check_ui_class.unregister()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
