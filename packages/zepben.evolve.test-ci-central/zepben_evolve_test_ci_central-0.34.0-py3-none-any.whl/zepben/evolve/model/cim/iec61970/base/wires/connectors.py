# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from __future__ import annotations

from zepben.evolve.model.cim.iec61970.base.core.conducting_equipment import ConductingEquipment

__all__ = ["Connector", "Junction", "BusbarSection"]


class Connector(ConductingEquipment):
    """
    A conductor, or group of conductors, with negligible impedance, that serve to connect other conducting equipment
    within a single substation and are modelled with a single logical terminal.
    """
    pass


class Junction(Connector):
    """
    A point where one or more conducting equipments are connected with zero resistance.
    """
    pass


class BusbarSection(Connector):
    """
    A conductor, or group of conductors, with negligible impedance, that serve to connect other conducting equipment within a single substation.
                                                                                                                                            
    Voltage measurements are typically obtained from voltage transformers that are connected to busbar sections. A bus bar section may have many
    physical terminals but for analysis is modelled with exactly one logical terminal.
    """
    pass
