# SPDX-FileCopyrightText: 2026-2026 Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: MIT

import dataclasses
from typing import Dict, List


@dataclasses.dataclass(frozen=True)
class SceneRescaleRules:
    target_unit_scale: float
    scale_object_position: bool
    scale_animation_location_channels: bool
    scale_rig: bool
    scale_user_view: bool
    scale_constraints: bool = True


@dataclasses.dataclass(frozen=True)
class LibraryUpdateTask:
    description: str
    old: List[str]
    new: str


@dataclasses.dataclass(frozen=True)
class ReloadTask(LibraryUpdateTask):
    path_type: str = "absolute"


@dataclasses.dataclass(frozen=True)
class CollectionRelinkTask(LibraryUpdateTask):
    old_collection: str
    new_collection: str
    object_scale_multipliers: Dict[str, float] = dataclasses.field(default_factory=dict)
    object_location_multipliers: Dict[str, float] = dataclasses.field(default_factory=dict)
    path_type: str = "as_before"
    scripts_to_run_on_update: List[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True)
class ProxyUpdateToCollectionTask(CollectionRelinkTask):
    old_proxy: str = ""


@dataclasses.dataclass(frozen=True)
class LibrariesUpdateRules:
    reload_tasks: List[ReloadTask]
    collection_relink_tasks: List[CollectionRelinkTask]
    proxy_update_to_collection_tasks: List[ProxyUpdateToCollectionTask] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True)
class SceneRulesBackwardCompatibility:
    scene_rescale_rules: SceneRescaleRules
    libraries_update_rules: LibrariesUpdateRules
