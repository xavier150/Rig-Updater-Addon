# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

import bpy

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
