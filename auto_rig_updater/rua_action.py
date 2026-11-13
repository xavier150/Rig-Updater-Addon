# SPDX-FileCopyrightText: 2019-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

import bpy

from . import bbpl


def update_action_backward_compatibility(print_log: bool = False) -> None:
    print("Start update_action_backward_compatibility")
    rig_updater = bbpl.backward_compatibility.rig_action_updater.RigActionUpdater()
    rig_updater.print_log = print_log

    for action in bpy.data.actions:
        if action.library is not None:
            continue

        ## Follow controllers rename
        print(f"Updating action: {action.name}")
        rig_updater.update_action_curve_data_path(action, ['"]["Follow_c_Head"]', '"]["Follow_Head"]'], '["follow_head"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Follow_c_Skull_02"]', '"]["Follow_Skull_02"]'], '"]["follow_skull_02"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Follow_c_Tongue_01"]', '"]["Follow_Tongue_01"]'], '"]["follow_tongue_01"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Follow_c_Jaw_down"]', '"]["Follow_Jaw_down"]'], '"]["follow_jaw_down"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Follow_c_Neck"]', '"]["Follow_Neck"]'], '"]["follow_neck"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Follow_c_Hand_L"]', '"]["Follow_Hand_L"]'], '"]["follow_hand_l"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Follow_c_Hand_R"]', '"]["Follow_Hand_R"]'], '"]["follow_hand_r"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Follow_c_Spine_02"]', '"]["Follow_Spine_02"]'], '"]["follow_spine_02"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Follow_c_Pelvis"]', '"]["Follow_Pelvis"]'], '"]["follow_pelvis"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Follow_c_Foot_L"]', '"]["Follow_Foot_L"]'], '"]["follow_foot_l"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Follow_c_Foot_R"]', '"]["Follow_Foot_R"]'], '"]["follow_foot_r"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Follow_c_Walk"]', '"]["Follow_Walk"]'], '"]["follow_walk"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Follow_c_Gravity"]', '"]["Follow_Gravity"]'], '"]["follow_gravity"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Follow_c_Root"]', '"]["Follow_Root"]'], '"]["follow_root"]', True)


        rig_updater.update_action_curve_data_path(action, ['"]["Follow_c_UpperLeg_L"]', '"]["Follow_UpperLeg_L"]'], '"]["follow_upperleg_l"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Follow_c_LowerLeg_L"]', '"]["Follow_LowerLeg_L"]'], '"]["follow_lowerleg_l"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Follow_c_UpperLeg_R"]', '"]["Follow_UpperLeg_R"]'], '"]["follow_upperleg_r"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Follow_c_LowerLeg_R"]', '"]["Follow_LowerLeg_R"]'], '"]["follow_lowerleg_r"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Follow_c_Pelvis"]', '"]["Follow_Pelvis"]'], '"]["follow_pelvis"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Follow_c_invert_Pelvis"]', '"]["Follow_invert_Pelvis"]'], '"]["follow_invert_pelvis"]', True)

        rig_updater.update_action_curve_data_path(action, ['"]["Follow Shoulder"]', '"]["Follow_Shoulder"]', '"]["rp_Follow_Spine_02"]', '"]["Follow_Spline"]'], '"]["follow_spline"]', True) 
        
        ## Snap controllers rename
        rig_updater.update_action_curve_data_path(action, ['"]["Snap_c_Head"]', '"]["Snap_Head"]'], '"]["snap_head"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Snap_c_Skull_02"]', '"]["Snap_Skull_02"]'], '"]["snap_skull_02"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Snap_c_Tongue_01"]', '"]["Snap_Tongue_01"]'], '"]["snap_tongue_01"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Snap_c_Jaw_down"]', '"]["Snap_Jaw_down"]'], '"]["snap_jaw_down"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Snap_c_Neck"]', '"]["Snap_Neck"]'], '"]["snap_neck"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Snap_c_Hand_L"]', '"]["Snap_Hand_L"]'], '"]["snap_hand_l"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Snap_c_Hand_R"]', '"]["Snap_Hand_R"]'], '"]["snap_hand_r"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Snap_c_Spine_02"]', '"]["Snap_Spine_02"]'], '"]["snap_spine_02"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Snap_c_Pelvis"]', '"]["Snap_Pelvis"]'], '"]["snap_pelvis"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Snap_c_Foot_L"]', '"]["Snap_Foot_L"]'], '"]["snap_foot_l"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Snap_c_Foot_R"]', '"]["Snap_Foot_R"]'], '"]["snap_foot_r"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Snap_c_Walk"]', '"]["Snap_Walk"]'], '"]["snap_walk"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Snap_c_Gravity"]', '"]["Snap_Gravity"]'], '"]["snap_gravity"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["Snap_c_Root"]', '"]["Snap_Root"]'], '"]["snap_root"]', True)

        ## IK controllers rename
        rig_updater.update_action_curve_data_path(action, ['"]["AlignUp"]'], '"]["align_up"]', True)
        rig_updater.update_action_curve_data_path(action, ['"]["IKBlend"]', '"]["IkBlend"]'], '"]["ik_blend"]', True)

        ## Curve Follow controllers rename
        rig_updater.update_action_curve_data_path(action, ['"]["CurveBlend"]'], '"]["curve_blend"]', True)

        ## Interp controllers rename
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_UpperArm_L"]'], 'pose.bones["c_Stretch_UpperArm_L"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_LowerArm_L"]'], 'pose.bones["c_Stretch_LowerArm_L"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_UpperArm_R"]'], 'pose.bones["c_Stretch_UpperArm_R"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_LowerArm_R"]'], 'pose.bones["c_Stretch_LowerArm_R"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_UpperLeg_L"]'], 'pose.bones["c_Stretch_UpperLeg_L"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_LowerLeg_L"]'], 'pose.bones["c_Stretch_LowerLeg_L"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_UpperLeg_R"]'], 'pose.bones["c_Stretch_UpperLeg_R"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_LowerLeg_R"]'], 'pose.bones["c_Stretch_LowerLeg_R"]', True)

        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_Thigh_R"]', 'pose.bones["c_Interp_c_Thigh_R.001"]'], 'pose.bones["c_Stretch_Thigh_R"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_Thigh_L"]', 'pose.bones["c_Interp_c_Thigh_L.001"]'], 'pose.bones["c_Stretch_Thigh_L"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_Thigh_R.001"]'], 'pose.bones["c_Stretch_Thigh_R"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_Thigh_L.001"]'], 'pose.bones["c_Stretch_Thigh_L"]', True)

        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_Tail_00"]'], 'pose.bones["c_Stretch_Tail_00"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_Tail_01"]'], 'pose.bones["c_Stretch_Tail_01"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_Tail_02"]'], 'pose.bones["c_Stretch_Tail_02"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_Tail_03"]'], 'pose.bones["c_Stretch_Tail_03"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_Tail_04"]'], 'pose.bones["c_Stretch_Tail_04"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_Tail_05"]'], 'pose.bones["c_Stretch_Tail_05"]', True)

        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_Tongue_00"]'], 'pose.bones["c_Stretch_Tongue_00"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_Tongue_01"]'], 'pose.bones["c_Stretch_Tongue_01"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_Tongue_02"]'], 'pose.bones["c_Stretch_Tongue_02"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_Tongue_03"]'], 'pose.bones["c_Stretch_Tongue_03"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_Tongue_04"]'], 'pose.bones["c_Stretch_Tongue_04"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Interp_c_Tongue_05"]'], 'pose.bones["c_Stretch_Tongue_05"]', True)

        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_invert_Pelvis"]'], 'pose.bones["c_Invert_Pelvis"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Tongue_01_Item"]'], 'pose.bones["c_Tongue_Item"]', True)

        ## Curve Hook controllers rename
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_hook_'], 'pose.bones["c_CurveHook_', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_CurveHook_Tongue_00'], 'pose.bones["c_CurveHook_Tongue_Root', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_CurveHook_Tongue_02'], 'pose.bones["c_CurveHook_Tongue_Mid_01', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_CurveHook_Tongue_06'], 'pose.bones["c_CurveHook_Tongue_Mid_02', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_CurveHook_Tongue_10'], 'pose.bones["c_CurveHook_Tongue_Mid_03', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_CurveHook_Tongue_14'], 'pose.bones["c_CurveHook_Tongue_Tip', True)

        ## Head controllers rename
        rig_updater.update_action_curve_data_path(action, ['pose.bones["Head_Item"]'], 'pose.bones["c_Head_Item"]', True)

        ## Eyes controllers rename
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Eye_ref_track_R"]'], 'pose.bones["Pole_Eye_R"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Eye_ref_track_L"]'], 'pose.bones["Pole_Eye_L"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["Eyebrow_Full_R"]'], 'pose.bones["c_Eyebrow_Full_R"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["Eyebrow_Full_L"]'], 'pose.bones["c_Eyebrow_Full_L"]', True)

        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Eye_blink_pose_Up_L"]', 'pose.bones["Eye_blink_pose_Up_L"]'], 'pose.bones["c_UpperEyeBlink_Pose_L"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Eye_blink_pose_Up_R"]', 'pose.bones["Eye_blink_pose_Up_R"]'], 'pose.bones["c_UpperEyeBlink_Pose_R"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Eye_blink_pose_Down_L"]', 'pose.bones["Eye_blink_pose_Down_L"]'], 'pose.bones["c_LowerEyeBlink_Pose_L"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Eye_blink_pose_Down_R"]', 'pose.bones["Eye_blink_pose_Down_R"]'], 'pose.bones["c_LowerEyeBlink_Pose_R"]', True)

        ## Maw controllers rename
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Lips_smile_pose_L"]', 'pose.bones["Lips_smile_pose_L"]'], 'pose.bones["c_LipsSmile_Pose_L"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Lips_smile_pose_R"]', 'pose.bones["Lips_smile_pose_R"]'], 'pose.bones["c_LipsSmile_Pose_R"]', True)

        rig_updater.update_action_curve_data_path(action, ['pose.bones["Lips_top_pose"]', 'pose.bones["c_Lips_top_pose"]'], 'pose.bones["c_UpperLips_Pose"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["Lips_bot_pose"]', 'pose.bones["c_Lips_bot_pose"]'], 'pose.bones["c_LowerLips_Pose"]', True)

        rig_updater.update_action_curve_data_path(action, ['pose.bones["Tongue_01_Item"]'], 'pose.bones["c_Tongue_Item"]', True)

        ## Paw controllers rename
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Paw_Press_pose_L"]', 'pose.bones["Paw_Press_pose_L"]'], 'pose.bones["c_Paw_Press_Pose_L"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_Paw_Press_pose_R"]', 'pose.bones["Paw_Press_pose_R"]'], 'pose.bones["c_Paw_Press_Pose_R"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["Ik_Foot_L"]["Raise heel"]'], 'pose.bones["Ik_Foot_L"]["raise_heel_action_eval"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["Ik_Foot_L"]["Spread toes"]'], 'pose.bones["Ik_Foot_L"]["spread_toes_action_eval"]', True)

        ## Camera controllers rename
        rig_updater.update_action_curve_data_path(action, ['pose.bones["Camera_FPV"]'], 'pose.bones["c_Camera_FPV"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["CameraLow_FPV"]'], 'pose.bones["c_CameraLow_FPV"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["Camera_TPV"]'], 'pose.bones["c_Camera_TPV"]', True)

        ## Game data controllers rename
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_BodyForward"]', 'pose.bones["BodyForward"]'], 'pose.bones["c_BaseBodyAim"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["FootPrint_L"]'], 'pose.bones["c_FootPrint_L"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["FootPrint_R"]'], 'pose.bones["c_FootPrint_R"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["Foot_Item_L"]'], 'pose.bones["c_Foot_Item_L"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["Foot_Item_R"]'], 'pose.bones["c_Foot_Item_R"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["Hand_Item_L"]'], 'pose.bones["c_Hand_Item_L"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["Hand_Item_R"]'], 'pose.bones["c_Hand_Item_R"]', True)

        ## Game data controllers rename
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_FlatLeftSoleZone"]'], 'pose.bones["c_FlatSoleZone_L"]', True)
        rig_updater.update_action_curve_data_path(action, ['pose.bones["c_FlatRightSoleZone"]'], 'pose.bones["c_FlatSoleZone_R"]', True)

        ## Old deprecated controllers
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_Hat"]', 'pose.bones["Hat"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_Glasses"]', 'pose.bones["Glasses"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_Eye_blink_pose_L"]', 'pose.bones["c_Eye_blink_pose_R"]'])

        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_Interp_Tail_00"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_Interp_Tail_01"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_Interp_Tail_02"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_Interp_Tail_03"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_Interp_Tail_04"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_Interp_Tail_05"]'])

        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_Interp_Tongue_00"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_Interp_Tongue_01"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_Interp_Tongue_02"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_Interp_Tongue_03"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_Interp_Tongue_04"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_Interp_Tongue_05"]'])

        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_hook_Tail_00"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_hook_Tail_01"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_hook_Tail_02"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_hook_Tail_03"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_hook_Tail_04"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_hook_Tail_05"]'])

        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_hook_Tongue_00"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_hook_Tongue_01"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_hook_Tongue_02"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_hook_Tongue_03"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_hook_Tongue_04"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_hook_Tongue_05"]'])

        ## Hidden Rig Points that should not be animate
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["rp_follow_', 'pose.bones["rp_Follow_'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["rp_parent_', 'pose.bones["rp_Parent_'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["rp_c_Eye', 'pose.bones["rp_Eye'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["rp_Interp_'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["rp_InterpParent_'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["rp_InterpChild_'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["rp_oldPelvis"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["DebugLine_PoleSub_Frontleg_R"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["DebugLine_PoleSub_Frontleg_L"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["DebugLine_Pole_Frontleg_R"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["DebugLine_Pole_Frontleg_L"]'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["rp_']) 

        ## Construction bones that should not be animate
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["cons_'])

        ## Old deprecated animate
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_Throat'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_Chin_01'])
        rig_updater.remove_action_curve_by_data_path(action, ['pose.bones["c_Chin_02'])

    print("End update_action_backward_compatibility")
    if print_log:
        rig_updater.print_update_log()
