# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

from typing import Tuple, Optional

import bpy


def get_target_armature(context: bpy.types.Context, target_object: str) -> Tuple[Optional[bpy.types.Object], Optional[str]]:
    if target_object:
        scene = context.scene
        if scene is None:
            return None, "No active scene to look up the target object."
        obj = scene.objects.get(target_object)
        if obj is None:
            return None, f"Object '{target_object}' was not found in the scene."
    else:
        obj = context.object
    if obj is None or not isinstance(obj.data, bpy.types.Armature):
        return None, "Select an armature or specify a target armature."
    return obj, None


def get_config_filepath(armature: bpy.types.Object, value: str) -> str:
    data = armature.data
    if not isinstance(data, bpy.types.Armature):
        raise ValueError(f"Object '{armature.name}' is not an armature.")
    return bpy.path.abspath(value, library=armature.library) if value.strip() else ""

   