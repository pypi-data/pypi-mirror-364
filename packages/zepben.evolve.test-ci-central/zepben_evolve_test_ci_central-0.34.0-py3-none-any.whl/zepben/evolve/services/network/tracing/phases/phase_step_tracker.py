# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.
from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, TypeVar, Dict, Set

from zepben.evolve.services.network.tracing.phases.phase_step import PhaseStep
from zepben.evolve.services.network.tracing.traversals.tracker import BaseTracker
if TYPE_CHECKING:
    from zepben.evolve import ConductingEquipment, SinglePhaseKind

T = TypeVar("T")

__all__ = ["PhaseStepTracker"]


class PhaseStepTracker(BaseTracker[PhaseStep]):
    """
    A specialised tracker that tracks the cores that have been visited on a piece of conducting equipment. When attempting to visit
    for the second time, this tracker will return false if the cores being tracked are a subset of those already visited.
    For example, if you visit A1 on cores 0, 1, 2 and later attempt to visit A1 on core 0, 1, visit will return false,
    but an attempt to visit on cores 2, 3 would return true as 3 has not been visited before.

    This tracker does not support null items.
    """

    visited: Dict[ConductingEquipment, Set[SinglePhaseKind]] = defaultdict(set)

    def has_visited(self, item: PhaseStep) -> bool:
        return item.phases.issubset(self.visited[item.conducting_equipment])

    def visit(self, item: PhaseStep) -> bool:
        visited_phases = self.visited[item.conducting_equipment]

        changed = False
        for phase in item.phases:
            changed = changed or phase not in visited_phases
            visited_phases.add(phase)

        return changed

    def clear(self):
        self.visited.clear()
