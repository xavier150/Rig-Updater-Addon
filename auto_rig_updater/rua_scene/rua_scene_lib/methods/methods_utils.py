# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

import os
from typing import List, Optional, Set, cast

import bpy

from ... import rua_scene_type


def absolute_path(path: str, library: Optional[bpy.types.Library] = None) -> str:
    return os.path.normpath(bpy.path.abspath(path, library=library))


def path_key(path: str, library: Optional[bpy.types.Library] = None) -> str:
    return os.path.normcase(absolute_path(path, library))


def collection_tree(root: bpy.types.Collection) -> List[bpy.types.Collection]:
    """Return the root collection and its descendants."""
    collections = [root]
    for child in root.children:
        collections.extend(collection_tree(child))
    return collections


def collection_parents(root: bpy.types.Collection) -> List[bpy.types.Collection]:
    """Find collections and scene roots that directly contain the collection."""
    candidates = list(bpy.data.collections) + [scene.collection for scene in bpy.data.scenes]
    return [parent for parent in candidates if root in parent.children[:]]


def library_dependencies(libraries: Set[bpy.types.Library]) -> Set[bpy.types.Library]:
    """Include linked dependencies of the libraries being replaced."""
    libraries = set(libraries)
    users = bpy.data.user_map()
    while True:
        dependencies: Set[bpy.types.Library] = set()
        for block, block_users in users.items():
            library = cast(Optional[bpy.types.Library], block.library)
            if library is not None and any(user.library in libraries for user in block_users):
                dependencies.add(library)
        if dependencies <= libraries:
            return libraries
        libraries.update(dependencies)


def cleanup_orphaned_source_overrides(source_libraries: Set[bpy.types.Library]) -> Set[bpy.types.Object]:
    """Remove unused source overrides and return object references whose names were freed."""
    users = bpy.data.user_map()
    unused_overrides = {
        block for block in users
        if cast(Optional[bpy.types.Library], block.library) is None and block.override_library is not None
        and block.override_library.reference is not None
        and block.override_library.reference.library in source_libraries
    }
    while True:
        removable = {
            block for block in unused_overrides
            if not block.use_fake_user and not block.use_extra_user and users[block] <= unused_overrides
        }
        if removable == unused_overrides:
            break
        unused_overrides = removable
    released_names = {
        block.override_library.reference for block in unused_overrides
        if isinstance(block, bpy.types.Object)
        and block.override_library is not None
        and isinstance(block.override_library.reference, bpy.types.Object)
        and block.name == block.override_library.reference.name
    }
    if unused_overrides:
        bpy.data.batch_remove(ids=list(unused_overrides))
    return released_names


def cleanup_relinked_libraries(
    libraries: Set[bpy.types.Library], source_libraries: Set[bpy.types.Library],
) -> None:
    """Remove orphaned source overrides and unused linked data."""
    cleanup_orphaned_source_overrides(source_libraries)
    users = bpy.data.user_map()
    unused = {block for block in users if block.library in libraries}
    while True:
        removable = {
            block for block in unused
            if not block.use_fake_user and not block.use_extra_user and users[block] <= unused
        }
        if removable == unused:
            break
        unused = removable
    retained_libraries = {block.library for block in users if block not in unused}
    empty_libraries = {
        library for library in libraries
        if library not in retained_libraries and not library.use_fake_user
    }
    if unused or empty_libraries:
        bpy.data.batch_remove(ids=list(unused | empty_libraries))


def relative_library_path(root: bpy.types.Collection, task: rua_scene_type.CollectionRelinkTask) -> bool:
    if task.path_type != "as_before":
        return task.path_type == "relative"
    reference = root.override_library.reference if root.override_library is not None else root
    if reference is None:
        raise RuntimeError(f"Collection '{root.name}' has no library override reference.")
    library = cast(Optional[bpy.types.Library], reference.library)
    return library is not None and library.filepath.startswith("//")


def remove_collection_hierarchy(
    root: bpy.types.Collection, objects: Optional[List[bpy.types.Object]] = None,
) -> None:
    """Remove local objects and collections in the hierarchy, leaving linked data intact."""
    collections = collection_tree(root)
    if objects is None:
        objects = list(root.all_objects)
    for obj in objects:
        if cast(Optional[bpy.types.Library], obj.library) is None:
            bpy.data.objects.remove(obj, do_unlink=True)
    for collection in reversed(collections):
        if cast(Optional[bpy.types.Library], collection.library) is None:
            bpy.data.collections.remove(collection)


def reference_name(obj: bpy.types.Object) -> str:
    """Use the linked reference name to match an override to its replacement."""
    override = obj.override_library
    if override is not None and isinstance(override.reference, bpy.types.Object):
        return override.reference.name
    return obj.name


def relink_objects(
    root: bpy.types.Collection, proxy: Optional[bpy.types.Object] = None,
) -> List[bpy.types.Object]:
    objects = list(root.all_objects)
    if proxy is not None and proxy not in objects:
        objects.append(proxy)
    return objects


def find_relink_collections(task: rua_scene_type.CollectionRelinkTask) -> List[bpy.types.Collection]:
    """Find source collections and validate destination paths before any replacement."""
    old_paths = {path_key(path) for path in task.old}
    destination = absolute_path(task.new)
    matches: List[bpy.types.Collection] = []
    for collection in bpy.data.collections:
        override = collection.override_library
        reference = override.reference if override is not None else collection
        if not isinstance(reference, bpy.types.Collection) or reference.name != task.old_collection:
            continue
        library = cast(Optional[bpy.types.Library], reference.library)
        if library is None or path_key(library.filepath, library.parent) not in old_paths:
            continue
        if override is not None and collection.users == 0 and not collection.use_extra_user:
            continue
        if override is not None or collection_parents(collection):
            matches.append(collection)
        elif any(obj.instance_collection == collection for obj in bpy.data.objects):
            raise ValueError(
                f"Collection '{collection.name}' is instanced by an object; "
                "convert the instance to a library override before relinking."
            )
    if matches and not os.path.isfile(destination):
        raise ValueError(f"Destination library was not found: '{destination}'.")
    if matches and any(relative_library_path(root, task) for root in matches):
        if not bpy.data.filepath:
            raise ValueError("Save the current .blend file before relinking with relative library paths.")
        # Reject cross-drive relative paths before removing any collection.
        bpy.path.relpath(destination)
    return matches
