# SPDX-FileCopyrightText: 2019-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

import bpy

from .. import bbpl


def update_mesh_skin_weight_backward_compatibility(select_only: bool = False) -> None:
    skin_updater = bbpl.backward_compatibility.skin_weight_mesh_updater.SkinWeightMeshUpdater()
    objects = bpy.context.selected_objects if select_only else bpy.data.objects

    for obj in objects:
        if obj.type == "MESH":
            skin_updater.update_mesh_skin_weight(obj, ['Twist01_UpperArm_L', 'Twist_01_UpperArm_L'], 'UpperArm_Twist_01_L')
            skin_updater.update_mesh_skin_weight(obj, ['Twist01_UpperArm_R', 'Twist_01_UpperArm_R'], 'UpperArm_Twist_01_R')
            skin_updater.update_mesh_skin_weight(obj, ['Twist01_LowerArm_L', 'Twist_01_LowerArm_L'], 'LowerArm_Twist_01_L')
            skin_updater.update_mesh_skin_weight(obj, ['Twist01_LowerArm_R', 'Twist_01_LowerArm_R'], 'LowerArm_Twist_01_R')
            skin_updater.update_mesh_skin_weight(obj, ['Twist01_LowerLeg_L', 'Twist_01_LowerLeg_L'], 'LowerLeg_Twist_01_L')
            skin_updater.update_mesh_skin_weight(obj, ['Twist01_LowerLeg_R', 'Twist_01_LowerLeg_R'], 'LowerLeg_Twist_01_R')


def get_used_vertex_groups(obj: bpy.types.Object) -> list[str]:
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


def get_vertex_groups_without_bones(armature: bpy.types.Object) -> dict[str, list[str]]:
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
