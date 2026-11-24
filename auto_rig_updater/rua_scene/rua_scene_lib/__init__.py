# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

import importlib

import bpy

from . import constraints
from . import object_state
from . import methods
from . import rua_scene_lib_utils

if "constraints" in locals():
    importlib.reload(constraints)
if "object_state" in locals():
    importlib.reload(object_state)
if "methods" in locals():
    importlib.reload(methods)
if "rua_scene_lib_utils" in locals():
    importlib.reload(rua_scene_lib_utils)


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)
    constraints.register()
    object_state.register()
    methods.register()


def unregister() -> None:
    methods.unregister()
    object_state.unregister()
    constraints.unregister()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
