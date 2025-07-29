# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from zepben.evolve.model.cim.iec61970.base.core.identified_object import IdentifiedObject

__all__ = ["RemotePoint"]


class RemotePoint(IdentifiedObject):
    """
    For a RTU remote points correspond to telemetered values or control outputs. Other units (e.g. control centers)
    usually also contain calculated values.
    """
    pass
