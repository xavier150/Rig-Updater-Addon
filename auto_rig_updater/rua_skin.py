# SPDX-FileCopyrightText: 2019-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

import bpy

from . import bbpl


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
