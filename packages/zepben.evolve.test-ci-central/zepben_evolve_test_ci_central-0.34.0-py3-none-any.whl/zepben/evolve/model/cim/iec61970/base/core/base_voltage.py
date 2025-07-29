# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from zepben.evolve.model.cim.iec61970.base.core.identified_object import IdentifiedObject

__all__ = ["BaseVoltage"]


class BaseVoltage(IdentifiedObject):
    """
    Defines a system base voltage which is referenced.
    """

    nominal_voltage: int = 0
    """The power system resource's base voltage."""

