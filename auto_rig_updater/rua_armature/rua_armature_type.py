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
    old: List[str]
    new: str
    remove_if_already_exists: bool


@dataclasses.dataclass(frozen=True)
class UpdateTask:
    description: str
    replace_operations: List[CompatibilityOperation]
    remove_operations: List[CompatibilityOperation]


@dataclasses.dataclass(frozen=True)
class MeshWeightBackwardCompatibility:
    update_tasks: List[UpdateTask]


@dataclasses.dataclass(frozen=True)
class RigControllersBackwardCompatibility:
    update_tasks: List[UpdateTask]
