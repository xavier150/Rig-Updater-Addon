# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

import dataclasses
from typing import List


@dataclasses.dataclass(frozen=True)
class SceneRescaleRules:
    target_unit_scale: float


@dataclasses.dataclass(frozen=True)
class LibraryUpdateTask:
    description: str
    old: List[str]
    new: str


@dataclasses.dataclass(frozen=True)
class SceneRulesBackwardCompatibility:
    scene_rescale_rules: SceneRescaleRules
    libraries_update_rules: List[LibraryUpdateTask]
