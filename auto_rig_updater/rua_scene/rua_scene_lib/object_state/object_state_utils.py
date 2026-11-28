# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

from typing import Dict, List, NamedTuple, Optional, Set, Tuple

import bpy
from mathutils import Matrix

from ... import rua_scene_type
from ..constraints import constraints_utils


class ObjectSnapshot(NamedTuple):
    """Store an object copy, local constraint names and additional collection memberships."""

    name: str
    reference_name: str
    backup: bpy.types.Object
    object_constraints: List[str]
    bone_constraints: Dict[str, List[str]]
    external_collections: List[bpy.types.Collection]


def capture_object_state(
    source: bpy.types.Object, reference_name: str, excluded_collections: Set[bpy.types.Collection],
    include_bone_constraints: bool = True,
) -> ObjectSnapshot:
    # Object.copy() can change inherited constraint flags.
    object_names, bone_names = constraints_utils.local_constraint_names(source, include_bone_constraints)
    return ObjectSnapshot(
        source.name, reference_name, source.copy(), object_names, bone_names,
        [collection for collection in source.users_collection if collection not in excluded_collections],
    )


def validate_object_animation(source: bpy.types.Object) -> None:
    """Reject NLA strips that cannot be preserved during collection relinking."""
    if source.animation_data is None:
        return
    for track in source.animation_data.nla_tracks:
        for strip in track.strips:
            if strip.type != 'CLIP' or len(strip.modifiers):
                raise ValueError(
                    f"Cannot preserve NLA strip '{strip.name}' on '{source.name}' during collection relinking."
                )


def copy_object_animation(source: bpy.types.Object, destination: bpy.types.Object) -> None:
    """Restore action/NLA assignments without migrating curves or replacing rig drivers."""
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


def restore_object_state(snapshot: ObjectSnapshot, destination: bpy.types.Object) -> None:
    copy_object_animation(snapshot.backup, destination)
    constraints_utils.copy_scene_constraints(
        snapshot.backup, destination, snapshot.object_constraints, snapshot.bone_constraints,
    )
    for collection in snapshot.external_collections:
        if destination not in collection.objects[:]:
            collection.objects.link(destination)


def capture_object_references(
    old_names: Dict[bpy.types.Object, str], snapshots: List[ObjectSnapshot],
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

    for obj in bpy.data.objects:
        if obj in old_names or obj.library is not None:
            continue
        if obj.parent in old_names:
            parents.append((obj, obj.matrix_world.copy()))
            capture(obj, "parent")
        constraints_utils.capture_references(obj.constraints, capture)
        if obj.pose is not None:
            for bone in obj.pose.bones:
                constraints_utils.capture_references(bone.constraints, capture)
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


def restore_object_references(
    references: List[Tuple[object, str, str]], parents: List[Tuple[bpy.types.Object, Matrix]],
    replacements: Dict[str, bpy.types.Object],
) -> None:
    mappings: Dict[bpy.types.Object, List[Tuple[List[str], str]]] = {}
    for owner, attribute, name in references:
        target = replacements.get(name)
        if target is None:
            continue
        setattr(owner, attribute, target)
        if attribute == "target":
            constraints_utils.remap_subtarget(owner, target, mappings)
    for obj, matrix in parents:
        obj.matrix_world = matrix


def restore_selection(
    view_layer: bpy.types.ViewLayer, selected_names: Set[str], active_name: Optional[str],
) -> None:
    view_layer.update()
    active = None
    for obj in view_layer.objects:
        if obj is None:
            print("[Rig Updater] Warning: a view-layer object is unavailable while restoring selection.")
            continue
        obj.select_set(obj.name_full in selected_names, view_layer=view_layer)
        if obj.name_full == active_name:
            active = obj
    view_layer.objects.active = active


def restore_pose_mode(active_name: str) -> None:
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


def capture_world_transforms(
    objects: List[bpy.types.Object], reference_names: Dict[bpy.types.Object, str],
) -> Dict[str, Matrix]:
    return {
        reference_names[obj]: obj.matrix_world.copy() for obj in objects
        if obj.override_library is not None and obj.parent is None
    }


def restore_world_transforms(
    transforms: List[Tuple[bpy.types.Object, Matrix]], view_layer: bpy.types.ViewLayer,
) -> None:
    """Restore only root overrides; children retain their new rig's local transforms."""
    for obj, matrix in transforms:
        if obj.override_library is not None and obj.parent is None:
            obj.matrix_world = matrix
    view_layer.update()


def apply_object_multipliers(
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
