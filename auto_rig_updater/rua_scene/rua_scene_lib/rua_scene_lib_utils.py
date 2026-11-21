# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

import os
from typing import Callable, Dict, List, Optional, Set, cast

import bpy

from ... import rua_json_utils
from .. import rua_scene_type


def parse_libraries_update_rules(value: object) -> rua_scene_type.LibrariesUpdateRules:
    if not isinstance(value, dict):
        raise ValueError("libraries_update_rules: expected an object.")
    mapping = cast(Dict[str, object], value)
    keys = set(mapping)
    if not keys or not keys <= {"reload_tasks", "collection_relink_tasks"}:
        raise ValueError("libraries_update_rules: expected reload_tasks and/or collection_relink_tasks.")
    libraries = rua_json_utils.require_dict(mapping, "libraries_update_rules", keys)

    def parse_task(value: object, location: str, collection: bool) -> rua_scene_type.LibraryUpdateTask:
        task_keys = {"description", "old", "new"}
        if collection:
            task_keys.update({"old_collection", "new_collection"})
        task = rua_json_utils.require_dict(value, location, task_keys)
        description = task["description"]
        if not isinstance(description, str):
            raise ValueError(f"{location}.description: expected a string.")
        old_paths = rua_json_utils.parse_old_names(task["old"], f"{location}.old")
        new_path = rua_json_utils.parse_new_name(task["new"], f"{location}.new")
        if any(os.path.splitext(path)[1].lower() != ".blend" for path in old_paths + [new_path]):
            raise ValueError(f"{location}: library paths must point to .blend files.")
        if collection:
            return rua_scene_type.CollectionRelinkTask(
                description, old_paths, new_path,
                rua_json_utils.parse_new_name(task["old_collection"], f"{location}.old_collection"),
                rua_json_utils.parse_new_name(task["new_collection"], f"{location}.new_collection"),
            )
        return rua_scene_type.LibraryUpdateTask(description, old_paths, new_path)

    reload_tasks = [
        parse_task(item, f"libraries_update_rules.reload_tasks[{index}]", False)
        for index, item in enumerate(rua_json_utils.require_list(
            libraries.get("reload_tasks", []), "libraries_update_rules.reload_tasks",
        ))
    ]
    collection_tasks: List[rua_scene_type.CollectionRelinkTask] = []
    for index, item in enumerate(rua_json_utils.require_list(
        libraries.get("collection_relink_tasks", []), "libraries_update_rules.collection_relink_tasks",
    )):
        task = parse_task(item, f"libraries_update_rules.collection_relink_tasks[{index}]", True)
        if not isinstance(task, rua_scene_type.CollectionRelinkTask):
            raise RuntimeError("Collection relink task parsing returned an invalid task.")
        collection_tasks.append(task)
    return rua_scene_type.LibrariesUpdateRules(reload_tasks, collection_tasks)


def absolute_path(path: str, library: Optional[bpy.types.Library] = None) -> str:
    return os.path.normpath(bpy.path.abspath(path, library=library))


def path_key(path: str, library: Optional[bpy.types.Library] = None) -> str:
    return os.path.normcase(absolute_path(path, library))


def restore_selection(
    view_layer: bpy.types.ViewLayer, selected_names: Set[str], active_name: Optional[str],
) -> None:
    view_layer.update()
    active = None
    for obj in view_layer.objects:
        if obj is None:
            print("[Rig Updater] Warning: a view-layer object is unavailable while restoring selection.")
            continue
        obj.select_set(obj.name_full in selected_names, view_layer=view_layer)
        if obj.name_full == active_name:
            active = obj
    view_layer.objects.active = active


def update_scene_libraries(
    configuration: rua_scene_type.SceneRulesBackwardCompatibility,
    warning_callback: Optional[Callable[[str], None]] = None,
) -> int:
    from .methods import reload_tasks_utils, relink_tasks_utils

    tasks = configuration.libraries_update_rules
    reload_tasks_utils.preflight_reload_tasks(tasks.reload_tasks, warning_callback)
    updated = relink_tasks_utils.relink_scene_collections(tasks.collection_relink_tasks)
    return updated + reload_tasks_utils.reload_scene_libraries(tasks.reload_tasks, warning_callback)
