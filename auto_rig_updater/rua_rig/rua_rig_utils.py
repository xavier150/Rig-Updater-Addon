# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

from typing import List, Union, cast

from .. import bbpl
from .. import rua_json_utils
from . import rua_rig_type


def _parse_rig_operation(item: object, location: str) -> rua_rig_type.RigControllerReplaceOperation:
    operation = rua_json_utils.require_dict(item, location, {"old", "new", "conflit_resolution"})
    old_names = rua_json_utils.parse_old_names(operation["old"], f"{location}.old")
    new_name = rua_json_utils.parse_new_name(operation["new"], f"{location}.new")
    resolution = operation["conflit_resolution"]
    options = bbpl.backward_compatibility.rig_action_updater.CONFLIT_RESOLUTIONS
    if not isinstance(resolution, str) or resolution not in options:
        raise ValueError(f"{location}.conflit_resolution: expected one of {', '.join(options)}.")
    return rua_rig_type.RigControllerReplaceOperation(old_names, new_name, resolution)


def load_rig_controllers_backward_compatibility(filepath: str) -> rua_rig_type.RigControllersBackwardCompatibility:
    document = rua_json_utils.require_dict(rua_json_utils.load_document(filepath), "JSON", {"update_tasks"})
    tasks: List[rua_rig_type.RigControllerUpdateTask] = []
    for index, item in enumerate(rua_json_utils.require_list(document["update_tasks"], "update_tasks")):
        location = f"update_tasks[{index}]"
        optional_keys = {
            "replace_channel_operations", "remove_channel_operations",
            "replace_bone_operations", "remove_bone_operations",
        }
        keys = {"description", "action_search"}
        if isinstance(item, dict):
            if "action_search" not in item:
                raise ValueError(f"{location}.action_search: required; expected all_actions, used_actions, or revelant_actions.")
            keys.update(key for key in optional_keys if key in item)
        task = rua_json_utils.require_dict(cast(object, item), location, keys)
        description = task["description"]
        if not isinstance(description, str):
            raise ValueError(f"{location}.description: expected a string.")
        search = task["action_search"]
        if not isinstance(search, str) or search not in (
            "all_actions", "all_action", "used_actions", "revelant_actions",
        ):
            raise ValueError(f"{location}.action_search: expected all_actions, used_actions, or revelant_actions.")
        if search == "all_action":
            search = "all_actions"
        sections: List[Union[rua_rig_type.ReplaceSection, rua_rig_type.RemoveSection]] = []
        for key, value in task.items():
            if key in ("replace_channel_operations", "replace_bone_operations"):
                target = "channel" if key == "replace_channel_operations" else "bone"
                sections.append(rua_rig_type.ReplaceSection(
                    target, rua_json_utils.parse_replacements(value, f"{location}.{key}", _parse_rig_operation),
                ))
            elif key in ("remove_channel_operations", "remove_bone_operations"):
                target = "channel" if key == "remove_channel_operations" else "bone"
                sections.append(rua_rig_type.RemoveSection(
                    target, rua_json_utils.parse_removals(value, f"{location}.{key}", rua_rig_type.RemovalOperation),
                ))
        tasks.append(rua_rig_type.RigControllerUpdateTask(description, sections, search))
    return rua_rig_type.RigControllersBackwardCompatibility(tasks)
