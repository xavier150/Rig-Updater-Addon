# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: SPDX:MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

try:
    import bpy
    import importlib

    from . import bbpl
    from . import bpl
    from . import config
    from . import rua_json_utils
    from . import rua_armature
    from . import rua_rig
    from . import rua_skin
    from . import rua_action
    from . import rua_check
    from . import rua_ui

    if "bpl" in locals():
        importlib.reload(bpl)
    if "bbpl" in locals():
        importlib.reload(bbpl)
    if "config" in locals():
        importlib.reload(config)
    if "rua_json_utils" in locals():
        importlib.reload(rua_json_utils)
    if "rua_armature" in locals():
        importlib.reload(rua_armature)
    if "rua_rig" in locals():
        importlib.reload(rua_rig)
    if "rua_skin" in locals():
        importlib.reload(rua_skin)
    if "rua_action" in locals():
        importlib.reload(rua_action)
    if "rua_check" in locals():
        importlib.reload(rua_check)
    if "rua_ui" in locals():
        importlib.reload(rua_ui)

    bl_info = {}


    # -------------------------------------------------------------------
    #   Register & Unregister
    # -------------------------------------------------------------------


    classes = (
    )


    def register() -> None:
        try:
            for cls in classes:
                bpy.utils.register_class(cls)

            bbpl.register()
            rua_armature.register()
            rua_rig.register()
            rua_skin.register()
            rua_action.register()
            rua_check.register()
            rua_ui.register()

        except Exception as _:
            import traceback
            print("Failed to register addon:")
            print("\033[91m" + "---------------------------------" + "\033[0m")
            traceback.print_exc()
            print("\033[91m" + "---------------------------------" + "\033[0m")


    def unregister() -> None:
        try:
            rua_ui.unregister()
            rua_check.unregister()
            rua_action.unregister()
            rua_skin.unregister()
            rua_rig.unregister()
            rua_armature.unregister()
            bbpl.unregister()

            for cls in reversed(classes):
                bpy.utils.unregister_class(cls)

        except Exception as _:
            import traceback
            print("Failed to unregister addon:")
            print("\033[91m" + "---------------------------------" + "\033[0m")
            traceback.print_exc()
            print("\033[91m" + "---------------------------------" + "\033[0m")


except Exception as _:
    import traceback
    print("Failed to import addon modules:")
    print("\033[91m" + "---------------------------------" + "\033[0m")
    traceback.print_exc()
    print("\033[91m" + "---------------------------------" + "\033[0m")

