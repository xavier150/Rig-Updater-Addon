# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

import importlib

import bpy

from . import rua_skin_class
from . import rua_skin_utils

if "rua_skin_utils" in locals():
    importlib.reload(rua_skin_utils)
if "rua_skin_class" in locals():
    importlib.reload(rua_skin_class)


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)

    rua_skin_class.register()


def unregister() -> None:
    rua_skin_class.unregister()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
