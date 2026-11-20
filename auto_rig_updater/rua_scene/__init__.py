# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

import importlib

import bpy

from . import rua_scene_type
from . import rua_scene_lib
from . import rua_scene_utils
from . import rua_scene_props
from . import rua_scene_class

if "rua_scene_type" in locals():
    importlib.reload(rua_scene_type)
if "rua_scene_lib" in locals():
    importlib.reload(rua_scene_lib)
if "rua_scene_utils" in locals():
    importlib.reload(rua_scene_utils)
if "rua_scene_props" in locals():
    importlib.reload(rua_scene_props)
if "rua_scene_class" in locals():
    importlib.reload(rua_scene_class)


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)
    rua_scene_lib.register()
    rua_scene_props.register()
    rua_scene_class.register()


def unregister() -> None:
    rua_scene_class.unregister()
    rua_scene_props.unregister()
    rua_scene_lib.unregister()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
