# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

try:
    import bpy
    import importlib
    from . import bpl
    from . import bbpl

    import importlib
    if "bpl" in locals():
        importlib.reload(bpl)
    if "bbpl" in locals():
        importlib.reload(bbpl)

    bl_info = {}



    classes = (
    )


    def register():
        try:
            for cls in classes:
                bpy.utils.register_class(cls)

            bbpl.register()

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


