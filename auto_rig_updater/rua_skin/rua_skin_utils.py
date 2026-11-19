# SPDX-FileCopyrightText: 2019-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

from typing import List

import bpy

from .. import bbpl
from .. import rua_json_utils
from . import rua_skin_type


def _parse_mesh_operation(item: object, location: str) -> rua_skin_type.MeshWeightReplaceOperation:
    operation = rua_json_utils.require_dict(item, location, {"old", "new", "conflit_resolution"})
    old_names = rua_json_utils.parse_old_names(operation["old"], f"{location}.old")
    new_name = rua_json_utils.parse_new_name(operation["new"], f"{location}.new")
    resolution = operation["conflit_resolution"]
    options = bbpl.backward_compatibility.skin_weight_mesh_updater.CONFLIT_RESOLUTIONS
    if not isinstance(resolution, str) or resolution not in options:
        raise ValueError(f"{location}.conflit_resolution: expected one of {', '.join(options)}.")
    return rua_skin_type.MeshWeightReplaceOperation(old_names, new_name, resolution)


def load_mesh_weight_backward_compatibility(filepath: str) -> rua_skin_type.MeshWeightBackwardCompatibility:
    return rua_skin_type.MeshWeightBackwardCompatibility(rua_json_utils.parse_update_tasks(
        rua_json_utils.load_document(filepath), _parse_mesh_operation,
        rua_skin_type.RemovalOperation, rua_skin_type.MeshWeightUpdateTask,
    ))


def get_armature_children_meshes(armature: bpy.types.Object) -> List[bpy.types.Object]:
    if not isinstance(armature.data, bpy.types.Armature):
        raise ValueError(f"Object '{armature.name}' is not an armature.")
    return [child for child in armature.children_recursive if child.type == 'MESH']

def update_mesh_skin_weight_backward_compatibility(
    objects: List[bpy.types.Object],
    configuration: rua_skin_type.MeshWeightBackwardCompatibility,
    print_log: bool = False,
) -> None:
    skin_updater = bbpl.backward_compatibility.skin_weight_mesh_updater.SkinWeightMeshUpdater()
    skin_updater.print_log = print_log

    print(f"Starting mesh skin weight update backward compatibility with {len(objects)} objects...")

    for obj in objects:
        if obj.type == "MESH":
            for task in configuration.update_tasks:
                for operation in task.replace_operations:
                    skin_updater.update_mesh_skin_weight(
                        obj, operation.old, operation.new, conflit_resolution=operation.conflit_resolution,
                    )
                for operation in task.remove_operations:
                    for old_name in operation.old:
                        group = obj.vertex_groups.get(old_name)
                        if group is not None:
                            obj.vertex_groups.remove(group)
                            skin_updater.remove_weights += 1
                            print(f'"{old_name}" removed from "{obj.name}".')

    skin_updater.print_update_log()


def get_used_vertex_groups(obj: bpy.types.Object) -> List[str]:
    mesh = obj.data
    if not isinstance(mesh, bpy.types.Mesh):
        raise ValueError(f"Object '{obj.name}' is not a mesh.")
    if mesh.is_editmode:
        raise ValueError(f"Exit Edit Mode on '{obj.name}' before checking its skin weights.")

    influenced_groups: set[int] = set()
    for vertex in mesh.vertices:
        for assignment in vertex.groups:
            if assignment.weight > 0.0:
                influenced_groups.add(assignment.group)

    return [group.name for group in obj.vertex_groups if group.index in influenced_groups]


def get_skin_check_error(armature: bpy.types.Object) -> str | None:
    if armature.type != 'ARMATURE':
        return f"Object '{armature.name}' is not an armature."

    meshes = [child for child in armature.children_recursive if child.type == 'MESH']
    if not meshes:
        return f"Armature '{armature.name}' has no mesh descendants."

    for obj in meshes:
        mesh = obj.data
        if not isinstance(mesh, bpy.types.Mesh):
            return f"Object '{obj.name}' is not a mesh."
        if mesh.is_editmode:
            return f"Exit Edit Mode on '{obj.name}' before checking its skin weights."
    return None


def get_vertex_groups_without_bones(armature: bpy.types.Object) -> dict[str, List[str]]:
    error = get_skin_check_error(armature)
    if error is not None:
        raise ValueError(error)

    armature_data = armature.data
    if not isinstance(armature_data, bpy.types.Armature):
        raise ValueError(f"Object '{armature.name}' has no armature data.")
    bone_names = {bone.name for bone in armature_data.bones}

    return {
        child.name: [name for name in get_used_vertex_groups(child) if name not in bone_names]
        for child in armature.children_recursive
        if child.type == 'MESH'
    }
