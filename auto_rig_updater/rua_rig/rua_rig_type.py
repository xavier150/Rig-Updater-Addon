# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

import dataclasses
from typing import List, Union


@dataclasses.dataclass(frozen=True)
class RigControllerReplaceOperation:
    old: List[str]
    new: str
    conflit_resolution: str


@dataclasses.dataclass(frozen=True)
class RemovalOperation:
    old: List[str]


@dataclasses.dataclass(frozen=True)
class ReplaceSection:
    target: str
    operations: List[RigControllerReplaceOperation]


@dataclasses.dataclass(frozen=True)
class RemoveSection:
    target: str
    operations: List[RemovalOperation]


@dataclasses.dataclass(frozen=True)
class RemoveStartingChannelSection:
    prefixes: List[str]


@dataclasses.dataclass(frozen=True)
class RemoveDeformBonesSection:
    pass


@dataclasses.dataclass(frozen=True)
class RigControllerUpdateTask:
    description: str
    sections: List[Union[
        ReplaceSection, RemoveSection, RemoveStartingChannelSection, RemoveDeformBonesSection,
    ]]
    action_search: str


@dataclasses.dataclass(frozen=True)
class RigControllersBackwardCompatibility:
    update_tasks: List[RigControllerUpdateTask]
