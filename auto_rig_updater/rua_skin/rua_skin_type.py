# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

import dataclasses
from typing import List


@dataclasses.dataclass(frozen=True)
class MeshWeightReplaceOperation:
    old: List[str]
    new: str
    conflit_resolution: str


@dataclasses.dataclass(frozen=True)
class RemovalOperation:
    old: List[str]


@dataclasses.dataclass(frozen=True)
class MeshWeightUpdateTask:
    description: str
    replace_operations: List[MeshWeightReplaceOperation]
    remove_operations: List[RemovalOperation]
    remove_starting_prefixes: List[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True)
class MeshWeightBackwardCompatibility:
    update_tasks: List[MeshWeightUpdateTask]
