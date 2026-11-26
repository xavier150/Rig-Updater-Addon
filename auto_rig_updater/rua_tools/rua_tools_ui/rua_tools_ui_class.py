# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

from typing import TYPE_CHECKING, Set

import bpy

if TYPE_CHECKING:
    import bpy.stub_internal.rna_enums as rna_enums

from ... import bpl
from ... import rua_action
from ... import rua_armature


def _print_action_search(armature: bpy.types.Object) -> None:
    print(f'[Rig Updater] Action search preview for armature "{armature.name}":')
    for search in ("all_actions", "used_actions", "revelant_actions", "revelant_and_used_actions"):
        print(f"{search}:")
        for action in rua_action.rua_action_utils.get_actions_for_search(armature, search):
            print(f"- {action.name}")


class RUA_OT_PreviewActionSearch(bpy.types.Operator):
    bl_idname = "rua.preview_action_search"
    bl_label = "Action Search (Active)"
    bl_description = "Print the actions selected by each search mode for the active armature"

    def execute(self, context: bpy.types.Context) -> "Set[rna_enums.OperatorReturnItems]":
        armature, error = rua_armature.rua_armature_utils.get_target_armature(context, "")
        if error is not None:
            print(bpl.color_set.yellow(f"[Rig Updater] Warning: {error}"))
            self.report({'WARNING'}, error)
            return {'CANCELLED'}
        if armature is None:
            raise RuntimeError("Target armature resolution returned no object.")

        _print_action_search(armature)
        self.report({'INFO'}, "Action search preview printed to the system console.")
        return {'FINISHED'}


class RUA_OT_PreviewActionSearchAll(bpy.types.Operator):
    bl_idname = "rua.preview_action_search_all"
    bl_label = "Action Search (All)"
    bl_description = "Print the actions selected by each search mode for every armature in the scene"

    def execute(self, context: bpy.types.Context) -> "Set[rna_enums.OperatorReturnItems]":
        if context.scene is None:
            self.report({'WARNING'}, "No active scene.")
            return {'CANCELLED'}
        armatures = [obj for obj in context.scene.objects if isinstance(obj.data, bpy.types.Armature)]
        if not armatures:
            message = "No armatures found in the scene."
            print(bpl.color_set.yellow(f"[Rig Updater] Warning: {message}"))
            self.report({'WARNING'}, message)
            return {'CANCELLED'}

        for armature in armatures:
            _print_action_search(armature)
        self.report({'INFO'}, "Action search previews printed to the system console.")
        return {'FINISHED'}


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
    RUA_OT_PreviewActionSearch,
    RUA_OT_PreviewActionSearchAll,
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
