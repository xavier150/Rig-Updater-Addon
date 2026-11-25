# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

from typing import List, Optional, cast

import bpy

from ... import rua_scene_type
from . import collection_relink_utils, methods_utils


def _proxy_object(
    root: bpy.types.Collection, task: rua_scene_type.ProxyUpdateToCollectionTask,
) -> bpy.types.Object:
    collection = root.override_library.reference if root.override_library is not None else root
    if not isinstance(collection, bpy.types.Collection):
        raise ValueError(f"Collection '{task.old_collection}' has no library override reference.")
    if not task.old_proxy:
        candidates = [
            obj for obj in bpy.data.objects
            if obj.type == 'ARMATURE'
            and cast(Optional[bpy.types.Library], obj.library) is None
            and obj.override_library is not None
            and isinstance(obj.override_library.reference, bpy.types.Object)
            and obj.override_library.reference in collection.all_objects[:]
        ]
        if len(candidates) != 1:
            names = ", ".join(sorted(obj.name for obj in candidates))
            raise ValueError(
                f"Expected exactly one local proxy armature for collection '{task.old_collection}', "
                f"found {len(candidates)}{': ' + names if names else ''}. "
                "Set old_proxy to select the correct override."
            )
        return candidates[0]
    proxy = bpy.data.objects.get(task.old_proxy)
    if proxy is None or proxy.type != 'ARMATURE' or cast(Optional[bpy.types.Library], proxy.library) is not None:
        raise ValueError(f"Local proxy armature '{task.old_proxy}' was not found.")
    reference = proxy.override_library.reference if proxy.override_library is not None else None
    if (
        not isinstance(reference, bpy.types.Object) or reference not in collection.all_objects[:]
    ):
        raise ValueError(
            f"Proxy '{task.old_proxy}' is not an override of an object in '{task.old_collection}'. "
            "Open the legacy file in Blender 3.5+ to convert its proxy to an override."
        )
    return proxy


def plan_proxy_updates(
    tasks: List[rua_scene_type.ProxyUpdateToCollectionTask],
) -> List[collection_relink_utils.CollectionRelinkPlan]:
    plans: List[collection_relink_utils.CollectionRelinkPlan] = []
    for task in tasks:
        matches = methods_utils.find_relink_collections(task)
        if not matches:
            plans.append(collection_relink_utils.CollectionRelinkPlan(task, matches))
            continue
        if len(matches) != 1:
            raise ValueError(f"Proxy migration requires one matching collection, found {len(matches)}.")
        destination = methods_utils.absolute_path(task.new)
        with bpy.data.libraries.load(destination, link=True) as (source, target):
            if task.new_collection not in source.collections:
                raise ValueError(f"Collection '{task.new_collection}' was not found in '{destination}'.")
            target.collections = [task.new_collection]
        collection = cast(Optional[bpy.types.Collection], target.collections[0])
        if collection is None:
            raise ValueError(f"Could not link collection '{task.new_collection}' from '{destination}'.")
        armatures = [obj for obj in collection.all_objects if obj.type == 'ARMATURE']
        if len(armatures) != 1:
            raise ValueError(
                f"Proxy migration requires exactly one destination armature "
                f"in collection '{task.new_collection}', found {len(armatures)}."
            )
        plans.append(collection_relink_utils.CollectionRelinkPlan(
            task, matches, _proxy_object(matches[0], task), armatures[0].name,
        ))
    return plans


def update_proxies_to_collections(tasks: List[rua_scene_type.ProxyUpdateToCollectionTask]) -> int:
    return collection_relink_utils.apply_collection_relink_plans(plan_proxy_updates(tasks))
