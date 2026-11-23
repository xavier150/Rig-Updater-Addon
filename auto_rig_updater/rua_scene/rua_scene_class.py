# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

from typing import TYPE_CHECKING, List, Set

import bpy

if TYPE_CHECKING:
    import bpy.stub_internal.rna_enums as rna_enums

from .. import bpl
from . import rua_scene_utils
from .rua_scene_lib import rua_scene_lib_utils


class RUA_OT_UpdateSceneLibraries(bpy.types.Operator):
    bl_idname = "rua.update_scene_libraries"
    bl_label = "Update Scene Libraries"
    bl_description = "Reload libraries or relink collections from the Scene Rules JSON"

    def execute(self, context: bpy.types.Context) -> "Set[rna_enums.OperatorReturnItems]":
        scene = context.scene
        if scene is None:
            self.report({'WARNING'}, "No active scene.")
            return {'CANCELLED'}
        configuration, error = rua_scene_utils.load_scene_configuration(scene)
        if error is not None:
            print(bpl.color_set.yellow(f"[Rig Updater] Warning: {error}"))
            self.report({'WARNING'}, error)
            return {'CANCELLED'}
        if configuration is None:
            raise RuntimeError("Scene configuration loading returned no configuration.")
        warnings: List[str] = []
        count = rua_scene_lib_utils.update_scene_libraries(configuration, warning_callback=warnings.append)
        if warnings:
            self.report({'WARNING'}, f"Updated {count} libraries with warnings. See the system console.")
        else:
            self.report({'INFO'}, f"Updated {count} libraries.")
        return {'FINISHED'}


class RUA_OT_UpdateSceneScale(bpy.types.Operator):
    bl_idname = "rua.update_scene_scale"
    bl_label = "Update Scene Scale"
    bl_description = "Set the scene unit scale and rescale enabled data"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> "Set[rna_enums.OperatorReturnItems]":
        scene = context.scene
        if scene is None:
            self.report({'WARNING'}, "No active scene.")
            return {'CANCELLED'}
        configuration, error = rua_scene_utils.load_scene_configuration(scene)
        if error is not None:
            print(bpl.color_set.yellow(f"[Rig Updater] Warning: {error}"))
            self.report({'WARNING'}, error)
            return {'CANCELLED'}
        if configuration is None:
            raise RuntimeError("Scene configuration loading returned no configuration.")
        rua_scene_utils.update_scene_scale(scene, configuration)
        self.report({'INFO'}, "Updated the scene unit scale.")
        return {'FINISHED'}


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
    RUA_OT_UpdateSceneLibraries,
    RUA_OT_UpdateSceneScale,
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
