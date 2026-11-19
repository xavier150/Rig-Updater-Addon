# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

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
    return rua_rig_type.RigControllersBackwardCompatibility(rua_json_utils.parse_update_tasks(
        rua_json_utils.load_document(filepath), _parse_rig_operation,
        rua_rig_type.RemovalOperation, rua_rig_type.RigControllerUpdateTask,
    ))
