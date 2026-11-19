# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

import bpy


def get_config_filepath(armature: bpy.types.Object, value: str) -> str:
    data = armature.data
    if not isinstance(data, bpy.types.Armature):
        raise ValueError(f"Object '{armature.name}' is not an armature.")
    return bpy.path.abspath(value, library=armature.library) if value.strip() else ""
