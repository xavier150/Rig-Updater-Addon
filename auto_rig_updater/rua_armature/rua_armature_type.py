# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

# ----------------------------------------------
#  Rig Updater
#  https://github.com/xavier150/Rig-Updater-Addon
# ----------------------------------------------

import dataclasses
from typing import List


@dataclasses.dataclass(frozen=True)
class CompatibilityOperation:
    description: str
    old_data_path_substrings: List[str]
    new_data_path_substring: str
    remove_if_already_exists: bool


@dataclasses.dataclass(frozen=True)
class UpdateTask:
    replace_operations: List[CompatibilityOperation]
    remove_operations: List[CompatibilityOperation]


@dataclasses.dataclass(frozen=True)
class MeshWeightBackwardCompatibility:
    update_tasks: List[UpdateTask]


@dataclasses.dataclass(frozen=True)
class RigControllersBackwardCompatibility:
    update_tasks: List[UpdateTask]
