# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

import importlib

import bpy

from . import rua_action_utils
from . import rua_action_ui

if "rua_action_utils" in locals():
    importlib.reload(rua_action_utils)
if "rua_action_ui" in locals():
    importlib.reload(rua_action_ui)


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)

    rua_action_ui.register()


def unregister() -> None:
    rua_action_ui.unregister()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
