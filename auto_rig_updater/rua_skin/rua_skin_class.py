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


class RUA_OT_CheckMeshesWeights(bpy.types.Operator):
    bl_idname = "rua.check_meshes_weights"
    bl_label = "Check Meshes Weights (Active)"
    bl_description = "Find used mesh groups with no matching bone for the target armature"

    if TYPE_CHECKING:
        target_object: str
    else:
        target_object: bpy.props.StringProperty(
            name="Target Object",
            description="Armature to process; defaults to the active armature",
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


class RUA_OT_CheckMeshesWeightsAll(bpy.types.Operator):
    bl_idname = "rua.check_meshes_weights_all"
    bl_label = "Check Meshes Weights (All)"
    bl_description = "Find used mesh groups with no matching bone across scene armatures"

    def execute(self, context: bpy.types.Context) -> "Set[rna_enums.OperatorReturnItems]":
        if context.scene is None:
            self.report({'WARNING'}, "No active scene.")
            return {'CANCELLED'}
        armatures = [obj for obj in context.scene.objects if isinstance(obj.data, bpy.types.Armature)]
        return _check_armatures(self, armatures)


class RUA_OT_UpdateArmatureDeformBones(bpy.types.Operator):
    bl_idname = "rua.update_armature_deform_bones"
    bl_label = "Update Armature Deform Bones"
    bl_description = "Rename armature bones using Mesh Weights JSON rules"
    bl_options = {'REGISTER', 'UNDO'}

    if TYPE_CHECKING:
        target_object: str
    else:
        target_object: bpy.props.StringProperty(
            name="Target Object",
            description="Armature to process; defaults to the active armature",
            default="",
            options={'SKIP_SAVE'},
        )

    def execute(self, context: bpy.types.Context) -> "Set[rna_enums.OperatorReturnItems]":
        armature, error = rua_armature.rua_armature_utils.get_target_armature(context, self.target_object)
        if error is not None:
            print(bpl.color_set.yellow(f"[Rig Updater] Warning: {error}"))
            self.report({'WARNING'}, error)
            return {'CANCELLED'}
        if armature is None:
            raise RuntimeError("Target armature resolution returned no object.")

        filepath = rua_armature.rua_armature_utils.get_config_filepath(
            armature,
            rua_armature.rua_armature_props.get_object_armature_mesh_weight_backward_compatibility(armature),
            property_name="rua_armature_mesh_weight_backward_compatibility",
        )
        error = rua_json_utils.get_config_file_error(filepath)
        if error is not None:
            print(bpl.color_set.yellow(f"[Rig Updater] Warning: {error}"))
            self.report({'WARNING'}, error)
            return {'CANCELLED'}

        configuration = rua_skin_utils.load_mesh_weight_backward_compatibility(filepath)
        updated_count, conflicts = rua_skin_utils.update_armature_deform_bones_backward_compatibility(
            armature, configuration,
        )
        message = f"{updated_count} armature bone(s) renamed."
        if conflicts:
            message += f" {len(conflicts)} name conflict(s) skipped. See the system console."
            self.report({'WARNING'}, message)
        else:
            self.report({'INFO'}, message)
        return {'FINISHED'}


def _update_meshes_weights(
    operator: bpy.types.Operator, armature: bpy.types.Object, objects: List[bpy.types.Object],
) -> "Set[rna_enums.OperatorReturnItems]":
    filepath = rua_armature.rua_armature_utils.get_config_filepath(
        armature,
        rua_armature.rua_armature_props.get_object_armature_mesh_weight_backward_compatibility(armature),
        property_name="rua_armature_mesh_weight_backward_compatibility",
    )
    error = rua_json_utils.get_config_file_error(filepath)
    if error is not None:
        print(bpl.color_set.yellow(f"[Rig Updater] Warning: {error}"))
        operator.report({'WARNING'}, error)
        return {'CANCELLED'}
    configuration = rua_skin_utils.load_mesh_weight_backward_compatibility(filepath)
    rua_skin_utils.update_meshes_weights_backward_compatibility(objects, configuration)
    return {'FINISHED'}


class RUA_OT_UpdateMeshesWeightsBackwardCompatibility(bpy.types.Operator):
    bl_idname = "rua.update_meshes_weights_backward_compatibility"
    bl_label = "Update Weights (Auto)"
    bl_description = "Update descendant meshes using the armature's Mesh Weights JSON"
    bl_options = {'REGISTER', 'UNDO'}

    if TYPE_CHECKING:
        target_object: str
    else:
        target_object: bpy.props.StringProperty(
            name="Target Object",
            description="Armature to process; defaults to the active armature",
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
        return _update_meshes_weights(self, obj, objects)


class RUA_OT_UpdateMeshesWeightsBackwardCompatibilitySelectOnly(bpy.types.Operator):
    bl_idname = "rua.update_meshes_weights_backward_compatibility_select_only"
    bl_label = "Update Weight (Select)"
    bl_description = "Update selected meshes, parented or not, using the active armature's Mesh Weights JSON"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> "Set[rna_enums.OperatorReturnItems]":
        armature = context.object
        if armature is None or not isinstance(armature.data, bpy.types.Armature):
            message = "Make an armature active to update the selected meshes."
            print(bpl.color_set.yellow(f"[Rig Updater] Warning: {message}"))
            self.report({'WARNING'}, message)
            return {'CANCELLED'}

        objects = [obj for obj in context.selected_objects or [] if obj.type == 'MESH']
        if not objects:
            message = "Select at least one mesh to update its weights."
            print(bpl.color_set.yellow(f"[Rig Updater] Warning: {message}"))
            self.report({'WARNING'}, message)
            return {'CANCELLED'}
        for obj in objects:
            if isinstance(obj.data, bpy.types.Mesh) and obj.data.is_editmode:
                message = f"Exit Edit Mode on '{obj.name}' before updating its skin weights."
                print(bpl.color_set.yellow(f"[Rig Updater] Warning: {message}"))
                self.report({'WARNING'}, message)
                return {'CANCELLED'}
        return _update_meshes_weights(self, armature, objects)


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
    RUA_OT_CheckMeshesWeights,
    RUA_OT_CheckMeshesWeightsAll,
    RUA_OT_UpdateArmatureDeformBones,
    RUA_OT_UpdateMeshesWeightsBackwardCompatibility,
    RUA_OT_UpdateMeshesWeightsBackwardCompatibilitySelectOnly,
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
