# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

from typing import TYPE_CHECKING, List, Set

import bpy

if TYPE_CHECKING:
    import bpy.stub_internal.rna_enums as rna_enums

from .. import bpl
from .. import rua_armature
from .. import rua_json_utils
from . import rua_skin_utils


def _check_armatures(operator: bpy.types.Operator, armatures: List[bpy.types.Object]) -> "Set[rna_enums.OperatorReturnItems]":
    if not armatures:
        message = "No armatures found in the scene."
        print(bpl.color_set.yellow(f"[Rig Updater] Warning: {message}"))
        operator.report({'WARNING'}, message)
        return {'CANCELLED'}

    checked_count = 0
    skipped_count = 0
    mesh_count = 0
    group_count = 0
    for armature in armatures:
        error = rua_skin_utils.get_skin_check_error(armature)
        if error is not None:
            print(bpl.color_set.yellow(f"[Rig Updater] Warning: {error}"))
            if len(armatures) == 1:
                operator.report({'WARNING'}, error)
                return {'CANCELLED'}
            skipped_count += 1
            continue

        results = rua_skin_utils.get_vertex_groups_without_bones(armature)
        checked_count += 1
        mesh_count += len(results)
        print(f"[Rig Updater] {armature.name}: checked {len(results)} mesh object(s).")
        for mesh_name, group_names in results.items():
            group_count += len(group_names)
            for name in group_names:
                print(bpl.color_set.yellow(
                    f'Warning; Mesh "{mesh_name}" Group "{name}" not found in the armature "{armature.name}"'
                ))

    if checked_count == 0:
        operator.report({'WARNING'}, "No armatures could be checked. See the system console.")
        return {'CANCELLED'}
    message = f"{group_count} used vertex groups without matching bones across {mesh_count} mesh object(s)."
    if len(armatures) > 1:
        message += f" {skipped_count} armature(s) not checked."
    message += " See the system console."
    operator.report({'WARNING'} if skipped_count else {'INFO'}, message)
    return {'FINISHED'}


class RUA_OT_CheckMeshWeights(bpy.types.Operator):
    bl_idname = "rua.check_skin_weights"
    bl_label = "Check Meshes Weights (Active)"
    bl_description = "Warn about used vertex groups with no matching bone in the target armature"

    if TYPE_CHECKING:
        target_object: str
    else:
        target_object: bpy.props.StringProperty(
            name="Target Object",
            description="Armature object name; leave empty to use the active armature",
            default="",
            options={'SKIP_SAVE'},
        )

    def execute(self, context: bpy.types.Context) -> "Set[rna_enums.OperatorReturnItems]":
        if self.target_object:
            scene = context.scene
            if scene is None:
                self.report({'WARNING'}, "No active scene to look up the target object.")
                return {'CANCELLED'}
            obj = scene.objects.get(self.target_object)
            if obj is None:
                self.report({'WARNING'}, f"Object '{self.target_object}' was not found in the scene.")
                return {'CANCELLED'}
        else:
            obj = context.object
            if obj is None:
                self.report({'WARNING'}, "Select an armature to check the skin weights of its meshes.")
                return {'CANCELLED'}

        return _check_armatures(self, [obj])


class RUA_OT_CheckMeshWeightsAll(bpy.types.Operator):
    bl_idname = "rua.check_skin_weights_all"
    bl_label = "Check Meshes Weights (All)"
    bl_description = "Warn about used vertex groups with no matching bone across all armatures in the scene"

    def execute(self, context: bpy.types.Context) -> "Set[rna_enums.OperatorReturnItems]":
        if context.scene is None:
            self.report({'WARNING'}, "No active scene.")
            return {'CANCELLED'}
        armatures = [obj for obj in context.scene.objects if isinstance(obj.data, bpy.types.Armature)]
        return _check_armatures(self, armatures)


class RUA_OT_UpdateMeshWeightBackwardCompatibility(bpy.types.Operator):
    bl_idname = "rua.update_mesh_skin_weight_backward_compatibility"
    bl_label = "Update Mesh Weights"
    bl_description = "Update vertex groups on meshes parented to the target armature for the newer rig"
    bl_options = {'REGISTER', 'UNDO'}

    if TYPE_CHECKING:
        target_object: str
    else:
        target_object: bpy.props.StringProperty(
            name="Target Object",
            description="Armature object name; leave empty to use the active armature",
            default="",
            options={'SKIP_SAVE'},
        )

    def execute(self, context: bpy.types.Context) -> "Set[rna_enums.OperatorReturnItems]":
        if self.target_object:
            scene = context.scene
            if scene is None:
                self.report({'WARNING'}, "No active scene to look up the target object.")
                return {'CANCELLED'}
            obj = scene.objects.get(self.target_object)
            if obj is None:
                self.report({'WARNING'}, f"Object '{self.target_object}' was not found in the scene.")
                return {'CANCELLED'}
        else:
            obj = context.object
            if obj is None:
                self.report({'WARNING'}, "Select an armature to update the skin weights of its meshes.")
                return {'CANCELLED'}

        error = rua_skin_utils.get_skin_check_error(obj)
        if error is not None:
            print(bpl.color_set.yellow(f"[Rig Updater] Warning: {error}"))
            self.report({'WARNING'}, error)
            return {'CANCELLED'}

        objects = rua_skin_utils.get_armature_children_meshes(obj)
        filepath = rua_armature.rua_armature_utils.get_config_filepath(
            obj,
            rua_armature.rua_armature_props.get_object_armature_mesh_weight_backward_compatibility(obj),
        )
        error = rua_json_utils.get_config_file_error(filepath)
        if error is not None:
            print(bpl.color_set.yellow(f"[Rig Updater] Warning: {error}"))
            self.report({'WARNING'}, error)
            return {'CANCELLED'}
        configuration = rua_skin_utils.load_mesh_weight_backward_compatibility(filepath)
        rua_skin_utils.update_mesh_skin_weight_backward_compatibility(objects, configuration)
        return {'FINISHED'}


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
    RUA_OT_CheckMeshWeights,
    RUA_OT_CheckMeshWeightsAll,
    RUA_OT_UpdateMeshWeightBackwardCompatibility,
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
