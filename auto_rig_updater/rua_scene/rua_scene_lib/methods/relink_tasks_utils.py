# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

from typing import List

import bpy

from ... import rua_scene_type
from . import methods_utils


def plan_collection_relinks(
    tasks: List[rua_scene_type.CollectionRelinkTask],
) -> List[methods_utils.CollectionRelinkPlan]:
    plans: List[methods_utils.CollectionRelinkPlan] = []
    for task in tasks:
        matches = methods_utils.find_relink_collections(task)
        if matches:
            destination = methods_utils.absolute_path(task.new)
            with bpy.data.libraries.load(destination, link=True) as (source, _):
                if task.new_collection not in source.collections:
                    raise ValueError(f"Collection '{task.new_collection}' was not found in '{destination}'.")
        plans.append(methods_utils.CollectionRelinkPlan(task, matches))
    return plans


def relink_scene_collections(tasks: List[rua_scene_type.CollectionRelinkTask]) -> int:
    return methods_utils.apply_collection_relink_plans(plan_collection_relinks(tasks))
