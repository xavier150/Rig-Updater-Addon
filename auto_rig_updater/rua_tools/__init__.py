# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

import importlib

import bpy

from . import rua_tools_ui

if "rua_tools_ui" in locals():
    importlib.reload(rua_tools_ui)


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)

    rua_tools_ui.register()


def unregister() -> None:
    rua_tools_ui.unregister()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
