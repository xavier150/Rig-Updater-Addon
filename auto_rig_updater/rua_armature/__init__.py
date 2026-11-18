# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

import importlib

import bpy

from . import rua_armature_class
from . import rua_armature_props
from . import rua_armature_type
from . import rua_armature_ui
from . import rua_armature_utils

if "rua_armature_type" in locals():
    importlib.reload(rua_armature_type)
if "rua_armature_props" in locals():
    importlib.reload(rua_armature_props)
if "rua_armature_utils" in locals():
    importlib.reload(rua_armature_utils)
if "rua_armature_class" in locals():
    importlib.reload(rua_armature_class)
if "rua_armature_ui" in locals():
    importlib.reload(rua_armature_ui)


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)

    rua_armature_class.register()
    rua_armature_props.register()
    rua_armature_ui.register()


def unregister() -> None:
    rua_armature_ui.unregister()
    rua_armature_props.unregister()
    rua_armature_class.unregister()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
