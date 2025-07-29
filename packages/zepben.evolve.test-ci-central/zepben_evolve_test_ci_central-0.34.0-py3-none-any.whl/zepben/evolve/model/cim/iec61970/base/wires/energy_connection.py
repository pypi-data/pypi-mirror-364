# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from zepben.evolve.model.cim.iec61970.base.core.conducting_equipment import ConductingEquipment

__all__ = ["EnergyConnection", "RegulatingCondEq"]


class EnergyConnection(ConductingEquipment):
    """
    A connection of energy generation or consumption on the power system phases.
    """
    pass


class RegulatingCondEq(EnergyConnection):
    """
    A short section of conductor with negligible impedance which can be manually removed and replaced if the circuit is
    de-energized. Note that zero-impedance branches can potentially be modeled by other equipment types.
    """

    control_enabled: bool = True
    """Specifies the regulation status of the equipment.  True is regulating, false is not regulating."""
