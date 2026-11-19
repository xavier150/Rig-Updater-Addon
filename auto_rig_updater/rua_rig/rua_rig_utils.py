# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

from typing import List, cast

from .. import rua_json_utils
from . import rua_rig_type


def _parse_rig_operation(item: object, location: str) -> rua_rig_type.RigControllerReplaceOperation:
    operation = rua_json_utils.require_dict(item, location, {"old", "new", "remove_if_already_exists"})
    old_names = rua_json_utils.parse_old_names(operation["old"], f"{location}.old")
    new_name = rua_json_utils.parse_new_name(operation["new"], f"{location}.new")
    remove_existing = operation["remove_if_already_exists"]
    if not isinstance(remove_existing, bool):
        raise ValueError(f"{location}.remove_if_already_exists: expected a boolean.")
    return rua_rig_type.RigControllerReplaceOperation(old_names, new_name, remove_existing)


def load_rig_controllers_backward_compatibility(filepath: str) -> rua_rig_type.RigControllersBackwardCompatibility:
    document = rua_json_utils.require_dict(rua_json_utils.load_document(filepath), "JSON", {"update_tasks"})
    tasks: List[rua_rig_type.RigControllerUpdateTask] = []
    for index, item in enumerate(rua_json_utils.require_list(document["update_tasks"], "update_tasks")):
        location = f"update_tasks[{index}]"
        keys = {"description", "replace_operations", "remove_operations"}
        if isinstance(item, dict) and "action_search" in item:
            keys.add("action_search")
        task = rua_json_utils.require_dict(cast(object, item), location, keys)
        search = task.get("action_search", "all_actions")
        if not isinstance(search, str) or search not in (
            "all_actions", "all_action", "used_actions", "revelant_actions",
        ):
            raise ValueError(f"{location}.action_search: expected all_actions, used_actions, or revelant_actions.")
        if search == "all_action":
            search = "all_actions"
        description, replacements, removals = rua_json_utils.parse_task_operations(
            task, location, _parse_rig_operation, rua_rig_type.RemovalOperation,
        )
        tasks.append(rua_rig_type.RigControllerUpdateTask(description, replacements, removals, search))
    return rua_rig_type.RigControllersBackwardCompatibility(tasks)
