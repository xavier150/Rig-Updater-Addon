# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

import json
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set, Tuple, TypeVar, cast

_Operation = TypeVar("_Operation")
_Removal = TypeVar("_Removal")
_Task = TypeVar("_Task")


def get_config_file_error(filepath: str) -> Optional[str]:
    if not filepath:
        return "Choose a backward compatibility JSON file in Config."
    path = Path(filepath)
    if path.suffix.lower() != ".json":
        return f"Expected a JSON file: '{filepath}'."
    if not path.is_file():
        return f"JSON file was not found: '{filepath}'."
    return None


def require_dict(value: object, location: str, keys: Set[str]) -> Dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{location}: expected an object.")
    mapping = cast(Dict[object, object], value)
    if set(mapping) != keys:
        raise ValueError(f"{location}: expected exactly these keys: {', '.join(sorted(keys))}.")
    return cast(Dict[str, object], mapping)


def require_list(value: object, location: str) -> List[object]:
    if not isinstance(value, list):
        raise ValueError(f"{location}: expected a list.")
    return cast(List[object], value)


def parse_old_names(value: object, location: str) -> List[str]:
    old_names = require_list(value, location)
    if not old_names or any(not isinstance(name, str) or not name for name in old_names):
        raise ValueError(f"{location}: expected a non-empty list of non-empty strings.")
    return [name for name in old_names if isinstance(name, str)]


def parse_new_name(value: object, location: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{location}: expected a non-empty string.")
    return value


def parse_update_tasks(
    value: object,
    parse_operation: Callable[[object, str], _Operation],
    removal_type: Callable[[List[str]], _Removal],
    task_type: Callable[[str, List[_Operation], List[_Removal]], _Task],
) -> List[_Task]:
    document = require_dict(value, "JSON", {"update_tasks"})
    tasks: List[_Task] = []
    for index, item in enumerate(require_list(document["update_tasks"], "update_tasks")):
        location = f"update_tasks[{index}]"
        task = require_dict(item, location, {"description", "replace_operations", "remove_operations"})
        description, replacements, removals = parse_task_operations(
            task, location, parse_operation, removal_type,
        )
        tasks.append(task_type(description, replacements, removals))
    return tasks


def parse_task_operations(
    task: Dict[str, object],
    location: str,
    parse_operation: Callable[[object, str], _Operation],
    removal_type: Callable[[List[str]], _Removal],
) -> Tuple[str, List[_Operation], List[_Removal]]:
    description = task["description"]
    if not isinstance(description, str):
        raise ValueError(f"{location}.description: expected a string.")
    replacements = [
        parse_operation(operation, f"{location}.replace_operations[{operation_index}]")
        for operation_index, operation in enumerate(
            require_list(task["replace_operations"], f"{location}.replace_operations")
        )
    ]
    removals: List[_Removal] = []
    removal_location = f"{location}.remove_operations"
    for removal_index, item in enumerate(require_list(task["remove_operations"], removal_location)):
        item_location = f"{removal_location}[{removal_index}]"
        operation = require_dict(item, item_location, {"old"})
        old_names = parse_old_names(operation["old"], f"{item_location}.old")
        removals.append(removal_type(old_names))
    return description, replacements, removals


def load_document(filepath: str) -> object:
    error = get_config_file_error(filepath)
    if error is not None:
        raise ValueError(error)
    with Path(filepath).open(encoding="utf-8-sig") as file:
        value: object = json.load(file)
    return value
