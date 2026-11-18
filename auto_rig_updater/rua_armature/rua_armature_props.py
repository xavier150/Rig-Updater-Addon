# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

import bpy


def get_object_armature_mesh_weight_backward_compatibility(obj: bpy.types.Object) -> str:
    value = getattr(obj, "rua_armature_mesh_weight_backward_compatibility")
    if not isinstance(value, str):
        raise TypeError("rua_armature_mesh_weight_backward_compatibility must be a file path.")
    return value


def get_object_armature_rig_controllers_backward_compatibility(obj: bpy.types.Object) -> str:
    value = getattr(obj, "rua_armature_rig_controllers_backward_compatibility")
    if not isinstance(value, str):
        raise TypeError("rua_armature_rig_controllers_backward_compatibility must be a file path.")
    return value


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)

    setattr(
        bpy.types.Object,
        "rua_armature_mesh_weight_backward_compatibility",
        bpy.props.StringProperty( # type: ignore
            name="Mesh Weights JSON",
            description="JSON migration rules for this armature's mesh vertex groups",
            subtype='FILE_PATH',
            options={'PATH_SUPPORTS_BLEND_RELATIVE'},
            default="",
        ),
    )
    setattr(
        bpy.types.Object,
        "rua_armature_rig_controllers_backward_compatibility",
        bpy.props.StringProperty( # type: ignore
            name="Rig Controllers JSON",
            description="JSON migration rules for animation FCurve data paths",
            subtype='FILE_PATH',
            options={'PATH_SUPPORTS_BLEND_RELATIVE'},
            default="",
        ),
    )


def unregister() -> None:
    delattr(bpy.types.Object, "rua_armature_rig_controllers_backward_compatibility")
    delattr(bpy.types.Object, "rua_armature_mesh_weight_backward_compatibility")

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
