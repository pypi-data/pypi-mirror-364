# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from typing import Optional

from zepben.evolve.model.cim.iec61970.base.core.terminal import Terminal
from zepben.evolve.services.network.tracing.traversals.tracker import Tracker

__all__ = ["AssociatedTerminalTracker"]


class AssociatedTerminalTracker(Tracker[Optional[Terminal]]):
    """A tracker that tracks the `ConductingEquipment` that owns the `Terminal` regardless of how it is visited."""

    def has_visited(self, terminal: Optional[Terminal]) -> bool:
        # Any terminal that does not have a valid conducting equipment reference is considered visited.
        if terminal is not None:
            if terminal.conducting_equipment is not None:
                return terminal.conducting_equipment in self.visited
        return True

    def visit(self, terminal: Optional[Terminal]) -> bool:
        # We don't visit any terminal that does not have a valid conducting equipment reference.
        if terminal is not None:
            if terminal.conducting_equipment is not None:
                if terminal.conducting_equipment in self.visited:
                    return False

                self.visited.add(terminal.conducting_equipment)
                return True
        return False
