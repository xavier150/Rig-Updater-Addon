# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

from typing import TYPE_CHECKING, Optional, Set, Tuple

import bpy

if TYPE_CHECKING:
    import bpy.stub_internal.rna_enums as rna_enums


_SCENE_PROPERTY = "rua_scene_rules_backward_compatibility"
_OBJECT_PROPERTIES = {
    "rua_armature_mesh_weight_backward_compatibility",
    "rua_armature_rig_controllers_backward_compatibility",
}


def _get_owner(
    context: bpy.types.Context, property_name: str, target_object: str,
) -> Tuple[Optional[bpy.types.ID], Optional[str]]:
    if property_name == _SCENE_PROPERTY:
        if context.scene is None:
            return None, "No active scene."
        return context.scene, None
    if property_name in _OBJECT_PROPERTIES:
        if context.scene is None:
            return None, "No active scene."
        owner = context.scene.objects.get(target_object)
        if owner is None or not isinstance(owner.data, bpy.types.Armature):
            return None, "The target armature could not be found."
        return owner, None
    return None, "Unsupported JSON configuration property."


class RUA_OT_SelectJsonFile(bpy.types.Operator):
    bl_idname = "rua.select_json_file"
    bl_label = "Select JSON File"
    bl_description = "Select a JSON configuration file"

    if TYPE_CHECKING:
        filepath: str
        filter_glob: str
        property_name: str
        target_object: str
    else:
        filepath: bpy.props.StringProperty(subtype='FILE_PATH')
        filter_glob: bpy.props.StringProperty(default="*.json;*.JSON", options={'HIDDEN'})
        property_name: bpy.props.StringProperty(options={'HIDDEN'})
        target_object: bpy.props.StringProperty(options={'HIDDEN'})

    def invoke(
        self, context: bpy.types.Context, event: Optional[bpy.types.Event],
    ) -> "Set[rna_enums.OperatorReturnItems]":
        del event
        owner, error = _get_owner(context, self.property_name, self.target_object)
        if error is not None:
            self.report({'WARNING'}, error)
            return {'CANCELLED'}
        if owner is None:
            raise RuntimeError("JSON file selector owner resolution returned no data.")
        if context.window_manager is None:
            self.report({'WARNING'}, "No active window manager.")
            return {'CANCELLED'}

        self.filepath = getattr(owner, self.property_name)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context: bpy.types.Context) -> "Set[rna_enums.OperatorReturnItems]":
        owner, error = _get_owner(context, self.property_name, self.target_object)
        if error is not None:
            self.report({'WARNING'}, error)
            return {'CANCELLED'}
        if owner is None:
            raise RuntimeError("JSON file selector owner resolution returned no data.")
        if not self.filepath.lower().endswith(".json"):
            self.report({'WARNING'}, "Select a .json file.")
            return {'CANCELLED'}

        setattr(owner, self.property_name, self.filepath)
        return {'FINISHED'}


def draw_path(layout: bpy.types.UILayout, owner: bpy.types.ID, property_name: str) -> None:
    row = layout.row(align=True)
    row.prop(owner, property_name)
    operator = row.operator("rua.select_json_file", text="", icon='FILE_FOLDER')
    operator.property_name = property_name
    operator.target_object = owner.name if property_name in _OBJECT_PROPERTIES else ""


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
    RUA_OT_SelectJsonFile,
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
