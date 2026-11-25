# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

from contextlib import ExitStack
from typing import Dict, List, NamedTuple, Optional, Set, cast

import bpy

from ... import rua_scene_type
from ..object_state import object_state_utils
from . import methods_utils


class CollectionRelinkPlan(NamedTuple):
    task: rua_scene_type.CollectionRelinkTask
    collections: List[bpy.types.Collection]
    proxy: Optional[bpy.types.Object] = None
    new_armature: str = ""


def _relink_collection(
    root: bpy.types.Collection, plan: CollectionRelinkPlan,
) -> bpy.types.Scene:
    """Replace one collection and restore matching objects' scene-local data."""
    task, _, proxy, new_armature = plan
    proxy_name = proxy.name if proxy is not None else None
    if proxy is not None and not new_armature:
        raise RuntimeError("Proxy migration requires a preflighted destination armature.")
    if bpy.context.mode == 'POSE':
        active = bpy.context.active_object
        if active is None or not bpy.ops.object.mode_set.poll():  # type: ignore[reportFunctionMemberAccess]
            raise RuntimeError("Cannot leave Pose Mode for collection relinking.")
        active_name = active.name
        replacement_name = active_name
        if active_name == proxy_name:
            replacement_name = new_armature
        if bpy.ops.object.mode_set(mode='OBJECT') != {'FINISHED'}:
            raise RuntimeError("Cannot leave Pose Mode for collection relinking.")
        with ExitStack() as stack:
            stack.callback(lambda: object_state_utils.restore_pose_mode(
                active_name if active_name in bpy.data.objects else replacement_name,
            ))
            return _relink_collection(root, plan)
    if bpy.context.mode != 'OBJECT':
        raise RuntimeError("Collection relinking requires Object Mode.")
    parents = methods_utils.collection_parents(root)
    if not parents or any(cast(Optional[bpy.types.Library], parent.library) is not None for parent in parents):
        raise ValueError(f"Collection '{root.name}' has no editable parent collection.")
    collections = set(methods_utils.collection_tree(root))
    old_objects = methods_utils.relink_objects(root, proxy)
    for obj in old_objects:
        if (
            obj != proxy and cast(Optional[bpy.types.Library], obj.library) is None
            and any(parent not in collections for parent in obj.users_collection)
        ):
            raise ValueError(f"Object '{obj.name}' is also used outside collection '{root.name}'.")
    scene = next((
        scene for scene in bpy.data.scenes
        if root in methods_utils.collection_tree(scene.collection)
    ), None)
    window = bpy.context.window
    if scene is None or window is None:
        raise RuntimeError(f"Collection '{root.name}' is not in a scene with an active window.")
    view_layer = window.view_layer if window.scene == scene else scene.view_layers[0]
    if view_layer is None:
        raise RuntimeError(f"No view layer is available for collection '{root.name}'.")
    if any(
        cast(Optional[bpy.types.Library], obj.library) is None and obj.name not in view_layer.objects
        for obj in old_objects
    ):
        raise RuntimeError(f"Collection '{root.name}' contains objects outside the active view layer.")

    selected_names = {obj.name_full for obj in view_layer.objects if obj.select_get(view_layer=view_layer)}
    active = view_layer.objects.active
    active_name = active.name_full if active is not None else None
    root_name = root.name
    relative_path = methods_utils.relative_library_path(root, task)
    local_objects = [
        obj for obj in old_objects if cast(Optional[bpy.types.Library], obj.library) is None
    ]
    old_names = {obj: methods_utils.reference_name(obj) for obj in local_objects}
    if proxy is not None:
        old_names[proxy] = new_armature
    if len(set(old_names.values())) != len(old_names):
        raise ValueError(f"Collection '{root_name}' contains multiple objects with the same reference name.")
    for obj in local_objects:
        object_state_utils.validate_object_animation(obj)
    snapshots: List[object_state_utils.ObjectSnapshot] = []
    removed = [False]
    completed = [False]

    def cleanup_snapshots() -> None:
        if removed[0] and not completed[0]:
            print("[Rig Updater] Warning: relinking failed after removing the old collection; reopen without saving.")
            return
        for snapshot in snapshots:
            bpy.data.objects.remove(snapshot.backup, do_unlink=True)

    with ExitStack() as stack:
        stack.callback(lambda: object_state_utils.restore_selection(view_layer, selected_names, active_name))
        stack.callback(setattr, window, "view_layer", window.view_layer)
        stack.callback(setattr, window, "scene", window.scene)
        stack.callback(cleanup_snapshots)
        window.scene = scene
        window.view_layer = view_layer
        view_layer.update()
        world_matrices = object_state_utils.capture_world_transforms(local_objects, old_names)
        for obj in local_objects:
            snapshots.append(object_state_utils.capture_object_state(
                obj, old_names[obj], collections, include_bone_constraints=obj != proxy,
            ))
        if proxy is not None:
            print(f"[Rig Updater] Rebuilding proxy '{proxy.name}' with the destination rig's drivers and bone constraints.")
        references, parent_matrices = object_state_utils.capture_object_references(old_names, snapshots)
        removed[0] = True
        if cast(Optional[bpy.types.Library], root.library) is not None:
            for parent in parents:
                parent.children.unlink(root)
        # Remove the old hierarchy before creating the new override.
        methods_utils.remove_collection_hierarchy(root, old_objects)
        view_layer.update()

        destination_path = methods_utils.absolute_path(task.new)
        with bpy.data.libraries.load(destination_path, link=True, relative=relative_path) as (source, target):
            if task.new_collection not in source.collections:
                raise ValueError(f"Collection '{task.new_collection}' was not found in '{destination_path}'.")
            target.collections = [task.new_collection]
        linked = cast(Optional[bpy.types.Collection], target.collections[0])
        if linked is None:
            raise RuntimeError(f"Could not link collection '{task.new_collection}' from '{destination_path}'.")
        library = cast(Optional[bpy.types.Library], linked.library)
        if library is not None:
            library.filepath = bpy.path.relpath(destination_path) if relative_path else destination_path
        existing = set(bpy.data.collections)
        instance = bpy.data.objects.new(task.new_collection, None)
        instance.instance_type = 'COLLECTION'
        instance.instance_collection = linked
        scene.collection.objects.link(instance)
        view_layer.update()
        for obj in view_layer.objects:
            obj.select_set(obj == instance, view_layer=view_layer)
        view_layer.objects.active = instance
        if not bpy.ops.object.make_override_library.poll():  # type: ignore[reportFunctionMemberAccess]
            bpy.data.objects.remove(instance, do_unlink=True)
            raise RuntimeError(f"Cannot create an override for collection '{task.new_collection}'.")
        result = bpy.ops.object.make_override_library()
        if result != {'FINISHED'}:
            raise RuntimeError(f"Failed to override collection '{task.new_collection}': {result}.")
        new_roots = [
            collection for collection in bpy.data.collections
            if collection not in existing and collection.override_library is not None
            and collection.override_library.reference == linked
        ]
        if len(new_roots) != 1:
            raise RuntimeError(f"Expected one new override of collection '{task.new_collection}'.")
        new_root = new_roots[0]
        new_objects: Dict[str, bpy.types.Object] = {}
        for obj in new_root.all_objects:
            name = methods_utils.reference_name(obj)
            if name in new_objects:
                raise ValueError(f"Collection '{task.new_collection}' has multiple objects named '{name}'.")
            new_objects[name] = obj
        pairs = [(snapshot, new_objects.get(snapshot.reference_name)) for snapshot in snapshots]
        for _, new in pairs:
            if new is not None:
                if cast(Optional[bpy.types.Library], new.library) is not None:
                    raise ValueError(f"Object '{new.name}' is linked and cannot receive scene data.")
        object_state_utils.restore_object_references(references, [], new_objects)
        for snapshot, new in pairs:
            if new is not None:
                object_state_utils.restore_object_state(snapshot, new)
        for parent in parents:
            if new_root not in parent.children[:]:
                parent.children.link(new_root)
        if scene.collection not in parents and new_root in scene.collection.children[:]:
            scene.collection.children.unlink(new_root)
        view_layer.update()
        object_state_utils.restore_world_transforms([
            (new_objects[name], matrix) for name, matrix in world_matrices.items()
            if name in new_objects
        ], view_layer)
        object_state_utils.restore_world_transforms(parent_matrices, view_layer)
        for snapshot in snapshots:
            bpy.data.objects.remove(snapshot.backup, do_unlink=True)
        snapshots.clear()
        new_root.name = task.new_collection if proxy_name is not None else root_name
        for snapshot, obj in pairs:
            if obj is not None and snapshot.name != proxy_name:
                obj.name = snapshot.name
        if proxy_name is not None:
            if proxy_name in selected_names:
                selected_names.remove(proxy_name)
                selected_names.add(new_armature)
            if active_name == proxy_name:
                active_name = new_armature
        completed[0] = True
    return scene


def apply_collection_relink_plans(plans: List[CollectionRelinkPlan]) -> int:
    """Validate all normal/proxy plans, then replace collections and clean unused libraries."""
    seen: Set[bpy.types.Collection] = set()
    seen_local_ids: Set[bpy.types.ID] = set()
    for task, matches, proxy, new_armature in plans:
        if seen.intersection(matches):
            raise ValueError(f"Collection '{task.old_collection}' is matched by multiple relink tasks.")
        for root in matches:
            objects = methods_utils.relink_objects(root, proxy)
            if proxy is not None:
                existing = bpy.data.objects.get(new_armature)
                if (
                    existing is not None and cast(Optional[bpy.types.Library], existing.library) is None
                    and existing not in objects
                ):
                    raise ValueError(f"Destination name '{new_armature}' is already used by a local object.")
            local_ids: Set[bpy.types.ID] = {
                item for item in methods_utils.collection_tree(root) + objects
                if cast(Optional[bpy.types.Library], item.library) is None
            }
            if seen_local_ids.intersection(local_ids):
                raise ValueError(f"Collection '{root.name}' overlaps another relink collection.")
            seen_local_ids.update(local_ids)
            for obj in objects:
                if cast(Optional[bpy.types.Library], obj.library) is None:
                    object_state_utils.validate_object_animation(obj)
        seen.update(matches)
    if bpy.app.version < (3, 5, 0) and any(plan.collections for plan in plans):
        raise ValueError("Collection relinking requires Blender 3.5 or newer.")
    source_libraries: Set[bpy.types.Library] = set()
    for root in seen:
        reference = root.override_library.reference if root.override_library is not None else root
        if reference is None:
            raise RuntimeError(f"Collection '{root.name}' has no library override reference.")
        library = cast(Optional[bpy.types.Library], reference.library)
        if library is not None:
            source_libraries.add(library)
    libraries = methods_utils.library_dependencies(source_libraries) if source_libraries else source_libraries
    updated = 0
    for plan in plans:
        scenes: Set[bpy.types.Scene] = set()
        for root in plan.collections:
            scenes.add(_relink_collection(root, plan))
            updated += 1
        object_state_utils.apply_object_multipliers(plan.task, scenes)
    if updated:
        methods_utils.cleanup_relinked_libraries(libraries)
    return updated
