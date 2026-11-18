# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

import json
from pathlib import Path
from typing import Dict, List, cast

import bpy

from . import rua_armature_type


def get_config_filepath(armature: bpy.types.Object, value: str) -> str:
    data = armature.data
    if not isinstance(data, bpy.types.Armature):
        raise ValueError(f"Object '{armature.name}' is not an armature.")
    return bpy.path.abspath(value, library=armature.library) if value.strip() else ""


def get_config_file_error(filepath: str) -> str | None:
    if not filepath:
        return "Choose a backward compatibility JSON file in Config."
    path = Path(filepath)
    if path.suffix.lower() != ".json":
        return f"Expected a JSON file: '{filepath}'."
    if not path.is_file():
        return f"JSON file was not found: '{filepath}'."
    return None


def _require_dict(value: object, location: str, keys: set[str]) -> Dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{location}: expected an object.")
    mapping = cast(Dict[object, object], value)
    if set(mapping) != keys:
        raise ValueError(f"{location}: expected exactly these keys: {', '.join(sorted(keys))}.")
    return cast(Dict[str, object], mapping)


def _require_list(value: object, location: str) -> List[object]:
    if not isinstance(value, list):
        raise ValueError(f"{location}: expected a list.")
    return cast(List[object], value)


def _parse_operations(
    value: object, location: str, replacing: bool,
) -> List[rua_armature_type.CompatibilityOperation]:
    operations: List[rua_armature_type.CompatibilityOperation] = []
    for index, item in enumerate(_require_list(value, location)):
        item_location = f"{location}[{index}]"
        operation = _require_dict(item, item_location, {
            "old", "new", "remove_if_already_exists",
        })
        old_names = _require_list(operation["old"], f"{item_location}.old")
        new_name = operation["new"]
        remove_existing = operation["remove_if_already_exists"]
        if not old_names or any(not isinstance(name, str) or not name for name in old_names):
            raise ValueError(f"{item_location}.old: expected a non-empty list of non-empty strings.")
        if not isinstance(new_name, str) or (replacing and not new_name):
            raise ValueError(f"{item_location}.new: expected {'a non-empty' if replacing else 'a'} string.")
        if not isinstance(remove_existing, bool):
            raise ValueError(f"{item_location}.remove_if_already_exists: expected a boolean.")
        operations.append(rua_armature_type.CompatibilityOperation(
            old=[name for name in old_names if isinstance(name, str)],
            new=new_name,
            remove_if_already_exists=remove_existing,
        ))
    return operations


def _parse_update_tasks(value: object) -> List[rua_armature_type.UpdateTask]:
    document = _require_dict(value, "JSON", {"update_tasks"})
    tasks: List[rua_armature_type.UpdateTask] = []
    for index, item in enumerate(_require_list(document["update_tasks"], "update_tasks")):
        location = f"update_tasks[{index}]"
        task = _require_dict(item, location, {"description", "replace_operations", "remove_operations"})
        description = task["description"]
        if not isinstance(description, str):
            raise ValueError(f"{location}.description: expected a string.")
        tasks.append(rua_armature_type.UpdateTask(
            description=description,
            replace_operations=_parse_operations(task["replace_operations"], f"{location}.replace_operations", True),
            remove_operations=_parse_operations(task["remove_operations"], f"{location}.remove_operations", False),
        ))
    return tasks


def _load_document(filepath: str) -> object:
    error = get_config_file_error(filepath)
    if error is not None:
        raise ValueError(error)
    with Path(filepath).open(encoding="utf-8-sig") as file:
        value: object = json.load(file)
    return value


def load_mesh_weight_backward_compatibility(filepath: str) -> rua_armature_type.MeshWeightBackwardCompatibility:
    return rua_armature_type.MeshWeightBackwardCompatibility(_parse_update_tasks(_load_document(filepath)))


def load_rig_controllers_backward_compatibility(filepath: str) -> rua_armature_type.RigControllersBackwardCompatibility:
    return rua_armature_type.RigControllersBackwardCompatibility(_parse_update_tasks(_load_document(filepath)))
