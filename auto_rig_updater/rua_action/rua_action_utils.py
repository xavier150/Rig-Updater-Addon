# SPDX-FileCopyrightText: 2019-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

import bpy

from .. import bbpl
from .. import rua_armature


def _controller_data_path(name: str) -> str:
    return f'pose.bones["{bpy.utils.escape_identifier(name)}"]'


def update_action_backward_compatibility(
    configuration: rua_armature.rua_armature_type.RigControllersBackwardCompatibility,
    print_log: bool = False,
) -> None:
    rig_updater = bbpl.backward_compatibility.rig_action_updater.RigActionUpdater()
    rig_updater.print_log = print_log

    print(f"Starting action update backward compatibility with {len(bpy.data.actions)} actions...")

    for action in bpy.data.actions:
        if action.library is not None:
            continue
        print(f"Updating action: {action.name}")
        for task in configuration.update_tasks:
            for operation in task.replace_operations:
                rig_updater.update_action_curve_data_path(
                    action,
                    [_controller_data_path(name) for name in operation.old],
                    _controller_data_path(operation.new),
                    operation.remove_if_already_exists,
                )
            for operation in task.remove_operations:
                rig_updater.remove_action_curve_by_data_path(
                    action, [_controller_data_path(name) for name in operation.old],
                )

    rig_updater.print_update_log()
