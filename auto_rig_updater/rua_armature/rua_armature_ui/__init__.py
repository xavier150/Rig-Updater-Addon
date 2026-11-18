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
from . import rua_armature_ui_utils

if "rua_armature_ui_utils" in locals():
    importlib.reload(rua_armature_ui_utils)


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)

    setattr(
        bpy.types.Scene,
        "rua_config_accordion",
        bbpl.blender_layout.layout_accordion.add_ui_accordion(name="Config"),
    )


def unregister() -> None:
    delattr(bpy.types.Scene, "rua_config_accordion")

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
