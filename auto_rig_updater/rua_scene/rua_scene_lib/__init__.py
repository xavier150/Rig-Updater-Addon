# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

import importlib

import bpy

from . import rua_scene_lib_utils
from . import methods

if "rua_scene_lib_utils" in locals():
    importlib.reload(rua_scene_lib_utils)
if "methods" in locals():
    importlib.reload(methods)


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)
    methods.register()


def unregister() -> None:
    methods.unregister()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
