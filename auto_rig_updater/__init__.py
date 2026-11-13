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
    from . import bpl
    from . import bbpl
    from . import config
    from . import rua_action
    from . import rua_skin
    from . import rua_ui

    import importlib
    if "bpl" in locals():
        importlib.reload(bpl)
    if "bbpl" in locals():
        importlib.reload(bbpl)
    if "config" in locals():
        importlib.reload(config)
    if "rua_action" in locals():
        importlib.reload(rua_action)
    if "rua_skin" in locals():
        importlib.reload(rua_skin)
    if "rua_ui" in locals():
        importlib.reload(rua_ui)

    bl_info = {}



    classes = (
    )


    def register():
        try:
            for cls in classes:
                bpy.utils.register_class(cls)

            bbpl.register()
            rua_ui.register()

        except Exception as _:
            import traceback
            print("Failed to register addon:")
            print("\033[91m" + "---------------------------------" + "\033[0m")
            traceback.print_exc()
            print("\033[91m" + "---------------------------------" + "\033[0m")


    def unregister():
        try:
            for cls in reversed(classes):
                bpy.utils.unregister_class(cls)

            rua_ui.unregister()
            bbpl.unregister()

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

