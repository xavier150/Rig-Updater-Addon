# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

import os
from typing import Callable, List, Optional, Set, Tuple, cast

import bpy

from ... import rua_json_utils
from .. import rua_scene_type


def parse_libraries_update_rules(value: object) -> List[rua_scene_type.LibraryUpdateTask]:
    libraries = rua_json_utils.require_dict(
        value, "libraries_update_rules", {"update_tasks"},
    )
    tasks: List[rua_scene_type.LibraryUpdateTask] = []
    for index, value in enumerate(rua_json_utils.require_list(
        libraries["update_tasks"], "libraries_update_rules.update_tasks",
    )):
        location = f"libraries_update_rules.update_tasks[{index}]"
        task = rua_json_utils.require_dict(value, location, {"description", "old", "new"})
        description = task["description"]
        if not isinstance(description, str):
            raise ValueError(f"{location}.description: expected a string.")
        old_paths = rua_json_utils.parse_old_names(task["old"], f"{location}.old")
        new_path = rua_json_utils.parse_new_name(task["new"], f"{location}.new")
        if any(os.path.splitext(path)[1].lower() != ".blend" for path in old_paths + [new_path]):
            raise ValueError(f"{location}: library paths must point to .blend files.")
        tasks.append(rua_scene_type.LibraryUpdateTask(description, old_paths, new_path))
    return tasks


def _absolute_path(path: str, library: Optional[bpy.types.Library] = None) -> str:
    return os.path.normpath(bpy.path.abspath(path, library=library))


def _path_key(path: str, library: Optional[bpy.types.Library] = None) -> str:
    return os.path.normcase(_absolute_path(path, library))


def _check_destination_library(
    library: bpy.types.Library, destination: str,
) -> List[Tuple[str, str]]:
    if not os.path.isfile(destination):
        raise ValueError(f"Destination library was not found: '{destination}'.")
    linked_blocks: Set[bpy.types.ID] = set()
    missing: List[Tuple[str, str]] = []
    with bpy.data.libraries.load(destination, link=True) as (source, _):
        for name in dir(source):
            available = getattr(source, name)
            blocks = getattr(bpy.data, name, None)
            if not isinstance(available, list) or blocks is None:
                continue
            for block in blocks:
                if not isinstance(block, bpy.types.ID) or block.library != library:
                    continue
                linked_blocks.add(block)
                if not block.is_library_indirect and block.name not in available:
                    missing.append((name, block.name))
    for users in bpy.data.user_map(subset=list(linked_blocks)).values():
        for user in users:
            user_library = cast(Optional[bpy.types.Library], user.library)
            if user_library is not None and user_library != library:
                raise ValueError(
                    f"Library '{library.filepath}' is also linked by '{user_library.filepath}'; "
                    "update that parent library to make the change persistent."
                )
    return missing


def update_scene_libraries(
    configuration: rua_scene_type.SceneRulesBackwardCompatibility,
    warning_callback: Optional[Callable[[str], None]] = None,
) -> int:
    library_paths = [
        (library, _path_key(library.filepath, library.parent))
        for library in bpy.data.libraries
    ]
    for task in configuration.libraries_update_rules:
        old_paths = {_path_key(path) for path in task.old}
        destination = _absolute_path(task.new)
        destination_key = _path_key(task.new)
        for index, (library, current_path) in enumerate(library_paths):
            if current_path in old_paths and current_path != destination_key:
                missing = _check_destination_library(library, destination)
                if missing:
                    warning = (
                        f"Library '{destination}' does not contain {len(missing)} linked data-blocks "
                        f"from '{library.filepath}'; Blender will handle them during relocation."
                    )
                    print(f"[Rig Updater] Warning: {warning}")
                    for kind, name in missing:
                        print(f'  {kind}: "{name}"')
                    if warning_callback is not None:
                        warning_callback(warning)
                library_paths[index] = (library, destination_key)

    updated = 0
    for task in configuration.libraries_update_rules:
        old_paths = {_path_key(path) for path in task.old}
        destination = _absolute_path(task.new)
        destination_key = _path_key(task.new)
        matches = [
            library for library in bpy.data.libraries
            if _path_key(library.filepath, library.parent) in old_paths
            and _path_key(library.filepath, library.parent) != destination_key
        ]
        names = [library.name for library in matches]
        for name in names:
            library = bpy.data.libraries.get(name)
            if library is None or _path_key(library.filepath, library.parent) not in old_paths:
                print(f'Library "{name}" is no longer available at its original path; skipped.')
                continue
            result = bpy.ops.wm.lib_relocate(  # type: ignore[reportUnknownMemberType]
                library=library.name, directory=os.path.dirname(destination),
                filename=os.path.basename(destination), relative_path=False,
            )
            if result != {'FINISHED'}:
                raise RuntimeError(f"Failed to relocate library '{name}' to '{destination}': {result}.")
            print(f'Library "{name}" relocated to "{destination}".')
            updated += 1
    return updated
