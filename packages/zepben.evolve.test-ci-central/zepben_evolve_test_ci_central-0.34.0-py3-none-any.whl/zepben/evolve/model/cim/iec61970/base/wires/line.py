# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from zepben.evolve.model.cim.iec61970.base.core.equipment_container import EquipmentContainer

__all__ = ["Line"]


class Line(EquipmentContainer):
    """Contains equipment beyond a substation belonging to a power transmission line."""
    pass
