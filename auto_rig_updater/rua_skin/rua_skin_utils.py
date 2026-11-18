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
from .. import rua_armature

def get_armature_children_meshes(armature: bpy.types.Object) -> List[bpy.types.Object]:
    if not isinstance(armature.data, bpy.types.Armature):
        raise ValueError(f"Object '{armature.name}' is not an armature.")
    return [child for child in armature.children_recursive if child.type == 'MESH']

def update_mesh_skin_weight_backward_compatibility(
    objects: List[bpy.types.Object],
    configuration: rua_armature.rua_armature_type.MeshWeightBackwardCompatibility,
    print_log: bool = False,
) -> None:
    skin_updater = bbpl.backward_compatibility.skin_weight_mesh_updater.SkinWeightMeshUpdater()
    skin_updater.print_log = print_log

    print(f"Starting mesh skin weight update backward compatibility with {len(objects)} objects...")

    for obj in objects:
        if obj.type == "MESH":
            for task in configuration.update_tasks:
                for operation in task.replace_operations:
                    for old_name in operation.old:
                        if old_name == operation.new:
                            continue
                        old_group = obj.vertex_groups.get(old_name)
                        if old_group is None:
                            continue
                        if obj.vertex_groups.get(operation.new) is not None:
                            if operation.remove_if_already_exists:
                                obj.vertex_groups.remove(old_group)
                                skin_updater.remove_weights += 1
                                print(f'"{old_name}" removed from "{obj.name}"; keeping "{operation.new}".')
                            else:
                                print(f'Warning; Mesh "{obj.name}" already has Group "{operation.new}"; keeping "{old_name}".')
                            continue
                        skin_updater.update_mesh_skin_weight(obj, [old_name], operation.new)
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
