# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

import dataclasses
from typing import List


@dataclasses.dataclass(frozen=True)
class SceneRescaleRules:
    target_unit_scale: float
    scale_object_position: bool
    scale_animation_location_channels: bool
    scale_rig: bool
    scale_user_view: bool


@dataclasses.dataclass(frozen=True)
class LibraryUpdateTask:
    description: str
    old: List[str]
    new: str


@dataclasses.dataclass(frozen=True)
class CollectionRelinkTask(LibraryUpdateTask):
    old_collection: str
    new_collection: str


@dataclasses.dataclass(frozen=True)
class LibrariesUpdateRules:
    reload_tasks: List[LibraryUpdateTask]
    collection_relink_tasks: List[CollectionRelinkTask]


@dataclasses.dataclass(frozen=True)
class SceneRulesBackwardCompatibility:
    scene_rescale_rules: SceneRescaleRules
    libraries_update_rules: LibrariesUpdateRules
