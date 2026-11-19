# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

import dataclasses
from typing import List


@dataclasses.dataclass(frozen=True)
class RigControllerReplaceOperation:
    old: List[str]
    new: str
    remove_if_already_exists: bool


@dataclasses.dataclass(frozen=True)
class RemovalOperation:
    old: List[str]


@dataclasses.dataclass(frozen=True)
class RigControllerUpdateTask:
    description: str
    replace_operations: List[RigControllerReplaceOperation]
    remove_operations: List[RemovalOperation]
    action_search: str = "all_actions"


@dataclasses.dataclass(frozen=True)
class RigControllersBackwardCompatibility:
    update_tasks: List[RigControllerUpdateTask]
