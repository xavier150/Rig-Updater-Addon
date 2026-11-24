# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

import os
import math
from typing import Callable, Dict, List, Optional, cast

from ... import rua_json_utils
from .. import rua_scene_type


def parse_libraries_update_rules(value: object) -> rua_scene_type.LibrariesUpdateRules:
    if not isinstance(value, dict):
        raise ValueError("libraries_update_rules: expected an object.")
    mapping = cast(Dict[str, object], value)
    keys = set(mapping)
    if not keys or not keys <= {
        "reload_tasks", "collection_relink_tasks", "proxy_update_to_collection_tasks",
    }:
        raise ValueError(
            "libraries_update_rules: expected reload_tasks, collection_relink_tasks "
            "and/or proxy_update_to_collection_tasks."
        )
    libraries = rua_json_utils.require_dict(mapping, "libraries_update_rules", keys)

    def parse_task(
        value: object, location: str, collection: bool, proxy: bool = False,
    ) -> rua_scene_type.LibraryUpdateTask:
        task_keys = {"description", "old", "new"}
        if collection:
            task_keys.update({"old_collection", "new_collection"})
            if proxy:
                task_keys.add("old_proxy")
            if isinstance(value, dict):
                task_keys.update(
                    key for key in ("object_scale_multipliers", "object_location_multipliers", "path_type")
                    if key in value
                )
        task = rua_json_utils.require_dict(value, location, task_keys)
        description = task["description"]
        if not isinstance(description, str):
            raise ValueError(f"{location}.description: expected a string.")
        old_paths = rua_json_utils.parse_old_names(task["old"], f"{location}.old")
        new_path = rua_json_utils.parse_new_name(task["new"], f"{location}.new")
        if any(os.path.splitext(path)[1].lower() != ".blend" for path in old_paths + [new_path]):
            raise ValueError(f"{location}: library paths must point to .blend files.")
        if collection:
            path_type = task.get("path_type", "as_before")
            if not isinstance(path_type, str) or path_type not in {"as_before", "relative", "absolute"}:
                raise ValueError(f"{location}.path_type: expected 'as_before', 'relative' or 'absolute'.")
            arguments = (
                description, old_paths, new_path,
                rua_json_utils.parse_new_name(task["old_collection"], f"{location}.old_collection"),
                rua_json_utils.parse_new_name(task["new_collection"], f"{location}.new_collection"),
                _parse_object_multipliers(
                    task.get("object_scale_multipliers", {}), f"{location}.object_scale_multipliers",
                ),
                _parse_object_multipliers(
                    task.get("object_location_multipliers", {}), f"{location}.object_location_multipliers",
                ),
                path_type,
            )
            if proxy:
                return rua_scene_type.ProxyUpdateToCollectionTask(
                    *arguments,
                    old_proxy=rua_json_utils.parse_new_name(task["old_proxy"], f"{location}.old_proxy"),
                )
            return rua_scene_type.CollectionRelinkTask(*arguments)
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
    proxy_tasks: List[rua_scene_type.ProxyUpdateToCollectionTask] = []
    for index, item in enumerate(rua_json_utils.require_list(
        libraries.get("proxy_update_to_collection_tasks", []),
        "libraries_update_rules.proxy_update_to_collection_tasks",
    )):
        task = parse_task(
            item, f"libraries_update_rules.proxy_update_to_collection_tasks[{index}]", True, proxy=True,
        )
        if not isinstance(task, rua_scene_type.ProxyUpdateToCollectionTask):
            raise RuntimeError("Proxy migration task parsing returned an invalid task.")
        proxy_tasks.append(task)
    return rua_scene_type.LibrariesUpdateRules(reload_tasks, collection_tasks, proxy_tasks)


def _parse_object_multipliers(value: object, location: str) -> Dict[str, float]:
    """Validate the name-to-factor mapping shared by local scale and location adjustments."""
    if not isinstance(value, dict):
        raise ValueError(f"{location}: expected an object.")
    multipliers: Dict[str, float] = {}
    for name, factor in cast(Dict[object, object], value).items():
        if not isinstance(name, str) or not name:
            raise ValueError(f"{location}: expected non-empty object names.")
        if (
            isinstance(factor, bool) or not isinstance(factor, (int, float))
            or not math.isfinite(factor) or factor <= 0
        ):
            raise ValueError(f"{location}.{name}: expected a finite positive number.")
        multipliers[name] = float(factor)
    return multipliers


def update_scene_libraries(
    configuration: rua_scene_type.SceneRulesBackwardCompatibility,
    warning_callback: Optional[Callable[[str], None]] = None,
) -> int:
    from .methods import collection_relink_utils, proxy_tasks_utils, reload_tasks_utils, relink_tasks_utils

    tasks = configuration.libraries_update_rules
    reload_tasks_utils.preflight_reload_tasks(tasks.reload_tasks, warning_callback)
    plans = [
        *relink_tasks_utils.plan_collection_relinks(tasks.collection_relink_tasks),
        *proxy_tasks_utils.plan_proxy_updates(tasks.proxy_update_to_collection_tasks),
    ]
    updated = collection_relink_utils.apply_collection_relink_plans(plans)
    return updated + reload_tasks_utils.reload_scene_libraries(tasks.reload_tasks, warning_callback)
