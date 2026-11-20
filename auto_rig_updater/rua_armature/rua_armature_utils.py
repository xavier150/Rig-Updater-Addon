# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

from typing import Tuple, Optional, cast

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


def get_config_filepath(
    armature: bpy.types.Object, value: str, property_name: Optional[str] = None,
) -> str:
    data = armature.data
    if not isinstance(data, bpy.types.Armature):
        raise ValueError(f"Object '{armature.name}' is not an armature.")
    if not value.strip():
        return ""
    library = cast(Optional[bpy.types.Library], armature.library)
    override = armature.override_library
    if library is None and override is not None:
        reference = override.reference
        if not isinstance(reference, bpy.types.Object):
            raise ValueError(f"Armature '{armature.name}' has no valid library override reference.")
        is_local = property_name is not None and (
            value != getattr(reference, property_name)
            or any(prop.rna_path == property_name for prop in override.properties)
        )
        if not is_local:
            library = reference.library
    return bpy.path.abspath(value, library=library)