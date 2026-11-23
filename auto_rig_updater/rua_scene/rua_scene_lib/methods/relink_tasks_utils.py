# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

import os
from contextlib import ExitStack
from typing import Dict, Iterable, List, NamedTuple, Optional, Set, Tuple, cast

import bpy
from mathutils import Matrix

from ... import rua_scene_type
from ..rua_scene_lib_utils import absolute_path, is_local_constraint, path_key, restore_selection


def _collection_tree(root: bpy.types.Collection) -> List[bpy.types.Collection]:
    """Return the root collection and its descendants."""
    collections = [root]
    for child in root.children:
        collections.extend(_collection_tree(child))
    return collections


def _collection_parents(root: bpy.types.Collection) -> List[bpy.types.Collection]:
    """Find collections and scene roots that directly contain the collection."""
    candidates = list(bpy.data.collections) + [scene.collection for scene in bpy.data.scenes]
    return [parent for parent in candidates if root in parent.children[:]]


def _library_dependencies(libraries: Set[bpy.types.Library]) -> Set[bpy.types.Library]:
    """Include linked dependencies of the libraries being replaced."""
    libraries = set(libraries)
    users = bpy.data.user_map()
    while True:
        dependencies = {
            block.library for block, block_users in users.items()
            if block.library is not None and any(user.library in libraries for user in block_users)
        }
        if dependencies <= libraries:
            return libraries
        libraries.update(dependencies)


def _cleanup_relinked_libraries(libraries: Set[bpy.types.Library]) -> None:
    """Remove only linked data with no surviving users outside the replaced libraries."""
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
        bpy.data.batch_remove(ids=unused | empty_libraries)


def _relative_library_path(root: bpy.types.Collection, task: rua_scene_type.CollectionRelinkTask) -> bool:
    if task.path_type != "as_before":
        return task.path_type == "relative"
    reference = root.override_library.reference if root.override_library is not None else root
    library = cast(Optional[bpy.types.Library], reference.library)
    return library is not None and library.filepath.startswith("//")


def _remove_collection_hierarchy(
    root: bpy.types.Collection, objects: Optional[List[bpy.types.Object]] = None,
) -> None:
    """Remove local objects and collections in the hierarchy, leaving linked data intact."""
    collections = _collection_tree(root)
    if objects is None:
        objects = list(root.all_objects)
    for obj in objects:
        if cast(Optional[bpy.types.Library], obj.library) is None:
            bpy.data.objects.remove(obj, do_unlink=True)
    for collection in reversed(collections):
        if cast(Optional[bpy.types.Library], collection.library) is None:
            bpy.data.collections.remove(collection)


def _reference_name(obj: bpy.types.Object) -> str:
    """Use the linked reference name to match an override to its replacement."""
    override = obj.override_library
    if override is not None and isinstance(override.reference, bpy.types.Object):
        return override.reference.name
    return obj.name


def _bone_name_mapping(obj: bpy.types.Object) -> List[Tuple[List[str], str]]:
    """Load controller and deform bone replacement operations from the new rig."""
    from ....rua_armature import rua_armature_props, rua_armature_utils
    from ....rua_rig import rua_rig_type, rua_rig_utils
    from ....rua_skin import rua_skin_utils

    mapping: List[Tuple[List[str], str]] = []
    if hasattr(obj, "rua_armature_rig_controllers_backward_compatibility"):
        value = rua_armature_props.get_object_armature_rig_controllers_backward_compatibility(obj)
        if value.strip():
            filepath = rua_armature_utils.get_config_filepath(
                obj, value, property_name="rua_armature_rig_controllers_backward_compatibility",
            )
            configuration = rua_rig_utils.load_rig_controllers_backward_compatibility(filepath)
            mapping.extend(
                (operation.old, operation.new)
                for task in configuration.update_tasks
                for section in task.sections
                if isinstance(section, rua_rig_type.ReplaceSection) and section.target == "bone"
                for operation in section.operations
            )
    if hasattr(obj, "rua_armature_mesh_weight_backward_compatibility"):
        value = rua_armature_props.get_object_armature_mesh_weight_backward_compatibility(obj)
        if value.strip():
            filepath = rua_armature_utils.get_config_filepath(
                obj, value, property_name="rua_armature_mesh_weight_backward_compatibility",
            )
            deform_configuration = rua_skin_utils.load_mesh_weight_backward_compatibility(filepath)
            mapping.extend(
                (operation.old, operation.new)
                for task in deform_configuration.update_tasks
                for operation in task.replace_operations
            )
    return mapping


def _new_bone_name(name: str, mapping: List[Tuple[List[str], str]]) -> str:
    """Apply bone replacement operations in order, including chained renames."""
    for old_names, new_name in mapping:
        if name in old_names:
            name = new_name
    return name


class _ObjectSnapshot(NamedTuple):
    """Store an object copy and the names of its scene-local constraints."""

    name: str
    reference_name: str
    backup: bpy.types.Object
    object_constraints: List[str]
    bone_constraints: Dict[str, List[str]]


def _copy_scene_constraints(snapshot: _ObjectSnapshot, destination: bpy.types.Object) -> None:
    """Restore local object and bone constraints, skipping bones absent from the new rig."""
    source = snapshot.backup
    for name in snapshot.object_constraints:
        destination.constraints.copy(source.constraints[name])
    if source.pose is None or destination.pose is None:
        return
    mapping = _bone_name_mapping(destination)
    for bone_name, names in snapshot.bone_constraints.items():
        destination_bone = destination.pose.bones.get(_new_bone_name(bone_name, mapping))
        if destination_bone is not None:
            for name in names:
                destination_bone.constraints.copy(source.pose.bones[bone_name].constraints[name])


def _validate_object_animation(source: bpy.types.Object) -> None:
    """Reject local drivers and NLA strips that cannot be preserved by relinking."""
    if source.animation_data is None:
        return
    reference = source.override_library.reference if source.override_library else None
    reference_animation = reference.animation_data if isinstance(reference, bpy.types.Object) else None
    reference_drivers: Set[Tuple[str, int]] = {
        (driver.data_path, driver.array_index)
        for driver in reference_animation.drivers
    } if reference_animation is not None else set()
    if any((driver.data_path, driver.array_index) not in reference_drivers
           for driver in source.animation_data.drivers):
        raise ValueError(
            f"Cannot persist local drivers on override object '{source.name}' during collection relinking."
        )
    for track in source.animation_data.nla_tracks:
        for strip in track.strips:
            if strip.type != 'CLIP' or strip.action is None or len(strip.modifiers):
                raise ValueError(
                    f"Cannot preserve NLA strip '{strip.name}' on '{source.name}' during collection relinking."
                )


def _copy_object_animation(source: bpy.types.Object, destination: bpy.types.Object) -> None:
    """Restore the action and NLA data without replacing the new rig's drivers."""
    from .... import bbpl

    if source.animation_data is None:
        return
    animation = bbpl.anim_utils.AnimationManagment()
    animation.save_animation_data(source)
    animation.set_animation_data(destination, copy_nla=True)
    if bpy.app.version >= (4, 4, 0) and destination.animation_data is not None:
        for source_track, destination_track in zip(
            source.animation_data.nla_tracks, destination.animation_data.nla_tracks,
        ):
            for source_strip, destination_strip in zip(source_track.strips, destination_track.strips):
                if source_strip.action_slot is not None:
                    destination_strip.action_slot = source_strip.action_slot


def _capture_object_references(
    old_names: Dict[bpy.types.Object, str], snapshots: List[_ObjectSnapshot],
) -> Tuple[List[Tuple[object, str, str]], List[Tuple[bpy.types.Object, Matrix]]]:
    """Record local references to old objects and parented objects' world transforms."""
    references: List[Tuple[object, str, str]] = []
    parents: List[Tuple[bpy.types.Object, Matrix]] = []
    # Object.copy() redirects self-targeting bone constraints to the backup.
    reference_names = {snapshot.backup: snapshot.reference_name for snapshot in snapshots}
    reference_names.update(old_names)

    def capture(owner: object, attribute: str) -> None:
        value: object = getattr(owner, attribute, None)
        if isinstance(value, bpy.types.Object) and value in reference_names:
            references.append((owner, attribute, reference_names[value]))

    def capture_constraints(constraints: Iterable[bpy.types.Constraint]) -> None:
        for constraint in constraints:
            capture(constraint, "target")
            capture(constraint, "space_object")
            if isinstance(constraint, bpy.types.ArmatureConstraint):
                for item in constraint.targets:
                    capture(item, "target")

    for obj in bpy.data.objects:
        if obj in old_names or obj.library is not None:
            continue
        if obj.parent in old_names:
            parents.append((obj, obj.matrix_world.copy()))
            capture(obj, "parent")
        capture_constraints(obj.constraints)
        if obj.pose is not None:
            for bone in obj.pose.bones:
                capture_constraints(bone.constraints)
        if obj.animation_data is not None:
            for driver in obj.animation_data.drivers:
                for variable in driver.driver.variables:
                    for target in variable.targets:
                        capture(target, "id")
        for modifier in obj.modifiers:
            for prop in modifier.bl_rna.properties:
                if prop.type == 'POINTER' and not prop.is_readonly:
                    capture(modifier, prop.identifier)
    return references, parents


def _restore_object_references(
    references: List[Tuple[object, str, str]], parents: List[Tuple[bpy.types.Object, Matrix]],
    replacements: Dict[str, bpy.types.Object],
) -> None:
    """Retarget recorded references and restore world transforms after relinking."""
    mappings: Dict[bpy.types.Object, List[Tuple[List[str], str]]] = {}
    for owner, attribute, name in references:
        target = replacements.get(name)
        if target is None:
            continue
        setattr(owner, attribute, target)
        subtarget: object = getattr(owner, "subtarget", None)
        if attribute == "target" and isinstance(subtarget, str) and target.type == 'ARMATURE':
            if target not in mappings:
                mappings[target] = _bone_name_mapping(target)
            setattr(owner, "subtarget", _new_bone_name(subtarget, mappings[target]))
    for obj, matrix in parents:
        obj.matrix_world = matrix


def _restore_pose_mode(active_name: str) -> None:
    """Return to Pose Mode on the named armature when the context permits it."""
    view_layer = bpy.context.view_layer
    if view_layer is None:
        print(f"[Rig Updater] Warning: could not restore Pose Mode on '{active_name}'.")
        return
    obj = view_layer.objects.get(active_name)
    if obj is None or obj.type != 'ARMATURE' or bpy.context.mode != 'OBJECT':
        print(f"[Rig Updater] Warning: could not restore Pose Mode on '{active_name}'.")
        return
    view_layer.objects.active = obj
    obj.select_set(True)
    if not bpy.ops.object.mode_set.poll() or bpy.ops.object.mode_set(mode='POSE') != {'FINISHED'}:  # type: ignore[reportFunctionMemberAccess]
        print(f"[Rig Updater] Warning: could not restore Pose Mode on '{active_name}'.")


def _restore_world_transforms(
    transforms: List[Tuple[bpy.types.Object, Matrix]], view_layer: bpy.types.ViewLayer,
) -> None:
    """Restore only root overrides; children retain their new rig's local transforms."""
    for obj, matrix in transforms:
        if obj.override_library is not None and obj.parent is None:
            obj.matrix_world = matrix
    view_layer.update()


def _relink_collection(
    root: bpy.types.Collection, task: rua_scene_type.CollectionRelinkTask,
) -> bpy.types.Scene:
    """Replace one collection and restore matching objects' scene-local data."""
    if bpy.context.mode == 'POSE':
        active = bpy.context.active_object
        if active is None or not bpy.ops.object.mode_set.poll():  # type: ignore[reportFunctionMemberAccess]
            raise RuntimeError("Cannot leave Pose Mode for collection relinking.")
        active_name = active.name
        if bpy.ops.object.mode_set(mode='OBJECT') != {'FINISHED'}:
            raise RuntimeError("Cannot leave Pose Mode for collection relinking.")
        with ExitStack() as stack:
            stack.callback(_restore_pose_mode, active_name)
            return _relink_collection(root, task)
    if bpy.context.mode != 'OBJECT':
        raise RuntimeError("Collection relinking requires Object Mode.")
    parents = _collection_parents(root)
    if not parents or any(cast(Optional[bpy.types.Library], parent.library) is not None for parent in parents):
        raise ValueError(f"Collection '{root.name}' has no editable parent collection.")
    collections = set(_collection_tree(root))
    old_objects = list(root.all_objects)
    for obj in old_objects:
        if obj.library is None and any(parent not in collections for parent in obj.users_collection):
            raise ValueError(f"Object '{obj.name}' is also used outside collection '{root.name}'.")
    scene = next((
        scene for scene in bpy.data.scenes
        if root in _collection_tree(scene.collection)
    ), None)
    window = bpy.context.window
    if scene is None or window is None:
        raise RuntimeError(f"Collection '{root.name}' is not in a scene with an active window.")
    view_layer = window.view_layer if window.scene == scene else scene.view_layers[0]
    if view_layer is None:
        raise RuntimeError(f"No view layer is available for collection '{root.name}'.")
    if any(obj.library is None and obj.name not in view_layer.objects for obj in old_objects):
        raise RuntimeError(f"Collection '{root.name}' contains objects outside the active view layer.")

    selected_names = {obj.name_full for obj in view_layer.objects if obj.select_get(view_layer=view_layer)}
    active = view_layer.objects.active
    active_name = active.name_full if active is not None else None
    root_name = root.name
    relative_path = _relative_library_path(root, task)
    local_objects = [obj for obj in old_objects if obj.library is None]
    old_names = {obj: _reference_name(obj) for obj in local_objects}
    if len(set(old_names.values())) != len(old_names):
        raise ValueError(f"Collection '{root_name}' contains multiple objects with the same reference name.")
    for obj in local_objects:
        _validate_object_animation(obj)
    snapshots: List[_ObjectSnapshot] = []
    removed = [False]
    completed = [False]

    def cleanup_snapshots() -> None:
        if removed[0] and not completed[0]:
            print("[Rig Updater] Warning: relinking failed after removing the old collection; reopen without saving.")
            return
        for snapshot in snapshots:
            bpy.data.objects.remove(snapshot.backup, do_unlink=True)

    with ExitStack() as stack:
        stack.callback(restore_selection, view_layer, selected_names, active_name)
        stack.callback(setattr, window, "view_layer", window.view_layer)
        stack.callback(setattr, window, "scene", window.scene)
        stack.callback(cleanup_snapshots)
        window.scene = scene
        window.view_layer = view_layer
        view_layer.update()
        world_matrices = {
            _reference_name(obj): obj.matrix_world.copy() for obj in old_objects
            if obj.override_library is not None and obj.parent is None
        }
        for obj in local_objects:
            # Copying an object can change constraint override flags.
            bone_constraints = {
                bone.name: [constraint.name for constraint in bone.constraints if is_local_constraint(constraint)]
                for bone in obj.pose.bones
            } if obj.pose is not None else {}
            snapshots.append(_ObjectSnapshot(
                obj.name, old_names[obj], obj.copy(),
                [constraint.name for constraint in obj.constraints if is_local_constraint(constraint)],
                {name: constraints for name, constraints in bone_constraints.items() if constraints},
            ))
        references, parent_matrices = _capture_object_references(old_names, snapshots)
        removed[0] = True
        if cast(Optional[bpy.types.Library], root.library) is not None:
            for parent in parents:
                parent.children.unlink(root)
        # Remove the old hierarchy before creating the new override.
        _remove_collection_hierarchy(root, old_objects)
        view_layer.update()

        destination_path = absolute_path(task.new)
        with bpy.data.libraries.load(destination_path, link=True, relative=relative_path) as (source, target):
            if task.new_collection not in source.collections:
                raise ValueError(f"Collection '{task.new_collection}' was not found in '{destination_path}'.")
            target.collections = [task.new_collection]
        linked = cast(Optional[bpy.types.Collection], target.collections[0])
        if linked is None:
            raise RuntimeError(f"Could not link collection '{task.new_collection}' from '{destination_path}'.")
        if linked.library is not None:
            linked.library.filepath = bpy.path.relpath(destination_path) if relative_path else destination_path
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
            name = _reference_name(obj)
            if name in new_objects:
                raise ValueError(f"Collection '{task.new_collection}' has multiple objects named '{name}'.")
            new_objects[name] = obj
        pairs = [(snapshot, new_objects.get(snapshot.reference_name)) for snapshot in snapshots]
        for _, new in pairs:
            if new is not None:
                if cast(Optional[bpy.types.Library], new.library) is not None:
                    raise ValueError(f"Object '{new.name}' is linked and cannot receive scene data.")
        _restore_object_references(references, [], new_objects)
        for snapshot, new in pairs:
            if new is not None:
                _copy_object_animation(snapshot.backup, new)
                _copy_scene_constraints(snapshot, new)
        for parent in parents:
            if new_root not in parent.children[:]:
                parent.children.link(new_root)
        if scene.collection not in parents and new_root in scene.collection.children[:]:
            scene.collection.children.unlink(new_root)
        view_layer.update()
        _restore_world_transforms([
            (new_objects[name], matrix) for name, matrix in world_matrices.items()
            if name in new_objects
        ], view_layer)
        _restore_world_transforms(parent_matrices, view_layer)
        for snapshot in snapshots:
            bpy.data.objects.remove(snapshot.backup, do_unlink=True)
        snapshots.clear()
        new_root.name = root_name
        for snapshot, obj in pairs:
            if obj is not None:
                obj.name = snapshot.name
        completed[0] = True
    return scene


def _apply_object_multipliers(
    task: rua_scene_type.CollectionRelinkTask, scenes: Set[bpy.types.Scene],
) -> None:
    """Adjust named objects' local transforms once per task, inside or outside the collection."""
    for attribute, multipliers in (
        ("scale", task.object_scale_multipliers),
        ("location", task.object_location_multipliers),
    ):
        applied: Set[bpy.types.Object] = set()
        for scene in scenes:
            for name, factor in multipliers.items():
                obj = scene.objects.get(name)
                if obj is None or obj in applied:
                    continue
                applied.add(obj)
                if obj.library is not None:
                    print(f"[Rig Updater] Warning: cannot multiply {attribute} on linked object '{name}'.")
                    continue
                if attribute == "scale":
                    obj.scale *= factor
                else:
                    obj.location *= factor
    for scene in scenes:
        for view_layer in scene.view_layers:
            view_layer.update()


def relink_scene_collections(
    tasks: List[rua_scene_type.CollectionRelinkTask],
) -> int:
    """Preflight all collection tasks, then relink matches and return their count."""
    plans: List[Tuple[rua_scene_type.CollectionRelinkTask, List[bpy.types.Collection]]] = []
    seen: Set[bpy.types.Collection] = set()
    seen_local_ids: Set[bpy.types.ID] = set()
    for task in tasks:
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
            if override is not None or _collection_parents(collection):
                matches.append(collection)
            elif any(obj.instance_collection == collection for obj in bpy.data.objects):
                raise ValueError(
                    f"Collection '{collection.name}' is instanced by an object; "
                    "convert the instance to a library override before relinking."
                )
        if matches and not os.path.isfile(destination):
            raise ValueError(f"Destination library was not found: '{destination}'.")
        if matches and any(_relative_library_path(root, task) for root in matches):
            if not bpy.data.filepath:
                raise ValueError("Save the current .blend file before relinking with relative library paths.")
            # Reject cross-drive relative paths before removing any collection.
            bpy.path.relpath(destination)
        if matches:
            with bpy.data.libraries.load(destination, link=True) as (source, _):
                if task.new_collection not in source.collections:
                    raise ValueError(f"Collection '{task.new_collection}' was not found in '{destination}'.")
        if seen.intersection(matches):
            raise ValueError(f"Collection '{task.old_collection}' is matched by multiple relink tasks.")
        for root in matches:
            local_ids: Set[bpy.types.ID] = {
                item for item in _collection_tree(root) + list(root.all_objects)
                if cast(Optional[bpy.types.Library], item.library) is None
            }
            if seen_local_ids.intersection(local_ids):
                raise ValueError(f"Collection '{root.name}' overlaps another relink collection.")
            seen_local_ids.update(local_ids)
            for obj in root.all_objects:
                if cast(Optional[bpy.types.Library], obj.library) is None:
                    _validate_object_animation(obj)
        seen.update(matches)
        plans.append((task, matches))
    if bpy.app.version < (3, 5, 0) and any(matches for _, matches in plans):
        raise ValueError("Collection relinking requires Blender 3.5 or newer.")
    libraries = _library_dependencies({
        reference.library
        for root in seen
        for reference in [root.override_library.reference if root.override_library is not None else root]
        if reference.library is not None
    }) if seen else set()
    updated = 0
    for task, matches in plans:
        scenes: Set[bpy.types.Scene] = set()
        for root in matches:
            scenes.add(_relink_collection(root, task))
            updated += 1
        _apply_object_multipliers(task, scenes)
    if updated:
        _cleanup_relinked_libraries(libraries)
    return updated
