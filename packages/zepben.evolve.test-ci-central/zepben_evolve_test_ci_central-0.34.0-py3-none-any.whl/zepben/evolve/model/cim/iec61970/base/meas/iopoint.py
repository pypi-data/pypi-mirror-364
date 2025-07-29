# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from zepben.evolve.model.cim.iec61970.base.core.identified_object import IdentifiedObject

__all__ = ["IoPoint"]


class IoPoint(IdentifiedObject):
    """
    This class describes a measurement or control value.
    The purpose is to enable having attributes and associations common for measurement and control.
    """
    pass
