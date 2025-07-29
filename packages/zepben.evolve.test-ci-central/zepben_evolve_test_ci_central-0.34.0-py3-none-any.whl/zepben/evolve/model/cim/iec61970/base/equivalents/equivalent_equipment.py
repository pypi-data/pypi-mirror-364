# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from __future__ import annotations

from zepben.evolve.model.cim.iec61970.base.core.conducting_equipment import ConductingEquipment

__all__ = ["EquivalentEquipment"]


class EquivalentEquipment(ConductingEquipment):
    """
    The class represents equivalent objects that are the result of a network reduction. The class is the base for equivalent objects of different types.
    """
    pass
