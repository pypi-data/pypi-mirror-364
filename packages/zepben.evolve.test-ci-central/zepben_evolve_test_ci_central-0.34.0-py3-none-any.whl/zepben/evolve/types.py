# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.
from __future__ import annotations

from typing import Callable, Optional, TypeVar

from zepben.evolve.model.cim.iec61970.base.core.conducting_equipment import ConductingEquipment
from zepben.evolve.model.cim.iec61970.base.core.terminal import Terminal
from zepben.evolve.model.cim.iec61970.base.wires.single_phase_kind import SinglePhaseKind
from zepben.evolve.services.network.tracing.feeder.direction_status import DirectionStatus
from zepben.evolve.services.network.tracing.phases.phase_status import PhaseStatus
from zepben.evolve.services.network.tracing.traversals.traversal import Traversal

T = TypeVar("T")

__all__ = ["OpenTest", "QueueNext", "PhaseSelector", "DirectionSelector"]

OpenTest = Callable[[ConductingEquipment, Optional[SinglePhaseKind]], bool]
QueueNext = Callable[[T, Traversal[T]], None]
PhaseSelector = Callable[[Terminal], PhaseStatus]
DirectionSelector = Callable[[Terminal], DirectionStatus]
