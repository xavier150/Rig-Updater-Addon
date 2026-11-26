# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

from typing import List, Optional, cast

import bpy

from ... import rua_scene_type
from . import collection_relink_utils, methods_utils


def plan_collection_relinks(
    tasks: List[rua_scene_type.CollectionRelinkTask],
) -> List[collection_relink_utils.CollectionRelinkPlan]:
    plans: List[collection_relink_utils.CollectionRelinkPlan] = []
    for task in tasks:
        if isinstance(task, rua_scene_type.ProxyUpdateToCollectionTask):
            from . import proxy_tasks_utils

            plans.extend(proxy_tasks_utils.plan_proxy_updates([task]))
            continue
        matches = methods_utils.find_relink_collections(task)
        if matches:
            destination = methods_utils.absolute_path(task.new)
            with bpy.data.libraries.load(destination, link=True) as (source, target):
                if task.new_collection not in source.collections:
                    raise ValueError(f"Collection '{task.new_collection}' was not found in '{destination}'.")
                target.collections = [task.new_collection]
            collection = cast(Optional[bpy.types.Collection], target.collections[0])
            if collection is None:
                raise ValueError(f"Could not link collection '{task.new_collection}' from '{destination}'.")
            destination_armatures = [obj for obj in collection.all_objects if obj.type == 'ARMATURE']
            destination_names = {obj.name for obj in destination_armatures}
            proxy: Optional[bpy.types.Object] = None
            new_armature = ""
            for root in matches:
                reference = root.override_library.reference if root.override_library is not None else root
                if not isinstance(reference, bpy.types.Collection):
                    raise ValueError(f"Collection '{root.name}' has no library override reference.")
                old_armatures = [obj for obj in reference.all_objects if obj.type == 'ARMATURE']
                old_names = {obj.name for obj in old_armatures}
                candidates = [
                    obj for obj in bpy.data.objects
                    if obj.type == 'ARMATURE' and obj.library is None
                    and obj.override_library is not None
                    and obj.override_library.reference in old_armatures
                    and methods_utils.reference_name(obj) not in destination_names
                ]
                replacements = [obj for obj in destination_armatures if obj.name not in old_names]
                if candidates:
                    if len(matches) != 1 or len(candidates) != 1 or len(replacements) != 1:
                        raise ValueError(
                            f"Cannot determine the replacement armature for collection '{task.old_collection}': "
                            f"found {len(candidates)} unmatched local armatures and "
                            f"{len(replacements)} unmatched destination armatures."
                        )
                    proxy = candidates[0]
                    new_armature = replacements[0].name
            plans.append(collection_relink_utils.CollectionRelinkPlan(task, matches, proxy, new_armature))
        else:
            plans.append(collection_relink_utils.CollectionRelinkPlan(task, matches))
    return plans
