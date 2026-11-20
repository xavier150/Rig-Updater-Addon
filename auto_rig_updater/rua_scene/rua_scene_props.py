# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

from typing import TYPE_CHECKING, Set
if TYPE_CHECKING:
    from typing import Literal

import bpy



def get_scene_rules_filepath(scene: bpy.types.Scene) -> str:
    value = getattr(scene, "rua_scene_rules_backward_compatibility")
    if not isinstance(value, str):
        raise TypeError("rua_scene_rules_backward_compatibility must be a file path.")
    return bpy.path.abspath(value, library=scene.library) if value.strip() else ""


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = (
)


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)
    options: "Set[Literal['PATH_SUPPORTS_BLEND_RELATIVE']]" = (
        {'PATH_SUPPORTS_BLEND_RELATIVE'} if bpy.app.version >= (4, 5, 0) else set()
    )
    setattr(
        bpy.types.Scene,
        "rua_scene_rules_backward_compatibility",
        bpy.props.StringProperty(  # type: ignore
            name="Scene Rules JSON",
            description="JSON migration rules for scene units and linked libraries",
            subtype='FILE_PATH',
            options=options,  # type: ignore
            default="",
        ),
    )


def unregister() -> None:
    delattr(bpy.types.Scene, "rua_scene_rules_backward_compatibility")
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
