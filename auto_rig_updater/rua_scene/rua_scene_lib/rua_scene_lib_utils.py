# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

import os
from contextlib import ExitStack
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


def _report_warning(message: str, warning_callback: Optional[Callable[[str], None]]) -> None:
    print(f"[Rig Updater] Warning: {message}")
    if warning_callback is not None:
        warning_callback(message)


def _restore_selection(
    view_layer: bpy.types.ViewLayer, selected_names: Set[str], active_name: Optional[str],
) -> None:
    active = None
    for obj in view_layer.objects:
        obj.select_set(obj.name_full in selected_names, view_layer=view_layer)
        if obj.name_full == active_name:
            active = obj
    view_layer.objects.active = active


def _refresh_override_objects(
    objects: List[Tuple[str, str]], destination: str,
    warning_callback: Optional[Callable[[str], None]],
) -> None:
    for name, reference_name in objects:
        obj = next((obj for obj in bpy.data.objects if obj.name == name and not obj.library), None)
        override = obj.override_library if obj is not None else None
        reference = override.reference if override is not None else None
        if (
            obj is None or not isinstance(reference, bpy.types.Object)
            or reference.name != reference_name or not reference.library
            or _path_key(reference.library.filepath, reference.library.parent) != _path_key(destination)
        ):
            _report_warning(
                f"Override object '{name}' is no longer available from '{destination}'; not refreshed.",
                warning_callback,
            )
            continue
        context = next((
            (scene, view_layer) for scene in bpy.data.scenes for view_layer in scene.view_layers
            if any(candidate == obj for candidate in view_layer.objects)
        ), None)
        if context is None:
            _report_warning(
                f"Override object '{name}' is not in any view layer; not refreshed.", warning_callback,
            )
            continue
        scene, view_layer = context
        window = bpy.context.window
        if window is None:
            _report_warning(
                f"No active window to refresh override object '{name}'; not refreshed.", warning_callback,
            )
            continue
        selected_names = {item.name_full for item in view_layer.objects if item.select_get(view_layer=view_layer)}
        active = view_layer.objects.active
        active_name = active.name_full if active is not None else None
        with ExitStack() as stack:
            stack.callback(_restore_selection, view_layer, selected_names, active_name)
            stack.callback(setattr, window, "view_layer", window.view_layer)
            stack.callback(setattr, window, "scene", window.scene)
            # The operator polls the window's real active object and selection.
            window.scene = scene
            window.view_layer = view_layer
            for item in view_layer.objects:
                item.select_set(item == obj, view_layer=view_layer)
            view_layer.objects.active = obj
            can_refresh = bpy.ops.object.make_override_library.poll()
            result = bpy.ops.object.make_override_library() if can_refresh else {'CANCELLED'}
        if not can_refresh:
            _report_warning(
                f"Cannot refresh override object '{name}' in the current mode/context "
                f"(Blender {bpy.app.version_string}); not refreshed.",
                warning_callback,
            )
            continue
        if result != {'FINISHED'}:
            raise RuntimeError(f"Failed to refresh override object '{name}': {result}.")
        print(f"Library override '{name}' refreshed.")


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
                    _report_warning(warning, warning_callback)
                    for kind, name in missing:
                        print(f'  {kind}: "{name}"')
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
            overrides: List[Tuple[str, str]] = []
            for obj in bpy.data.objects:
                override = obj.override_library
                if obj.library or override is None:
                    continue
                reference = override.reference
                if not isinstance(reference, bpy.types.Object) or reference.library != library:
                    continue
                if bpy.app.version >= (3, 2, 0) and override.is_system_override:
                    continue
                overrides.append((obj.name, reference.name))
            result = bpy.ops.wm.lib_relocate(  # type: ignore[reportUnknownMemberType]
                library=library.name, directory=os.path.dirname(destination),
                filename=os.path.basename(destination), relative_path=False,
            )
            if result != {'FINISHED'}:
                raise RuntimeError(f"Failed to relocate library '{name}' to '{destination}': {result}.")
            _refresh_override_objects(overrides, destination, warning_callback)
            print(f'Library "{name}" relocated to "{destination}".')
            updated += 1
    return updated
