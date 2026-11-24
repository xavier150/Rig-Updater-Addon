# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

import importlib

import bpy

from . import methods_utils
from . import reload_tasks_utils
from . import relink_tasks_utils
from . import proxy_tasks_utils

if "methods_utils" in locals():
    importlib.reload(methods_utils)
if "reload_tasks_utils" in locals():
    importlib.reload(reload_tasks_utils)
if "relink_tasks_utils" in locals():
    importlib.reload(relink_tasks_utils)
if "proxy_tasks_utils" in locals():
    importlib.reload(proxy_tasks_utils)


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
