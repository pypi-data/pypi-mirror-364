# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from zepben.evolve import Location, AssetInfo
from zepben.evolve.model.cim.iec61970.base.core.identified_object import IdentifiedObject

__all__ = ['PowerSystemResource']


class PowerSystemResource(IdentifiedObject):
    """
    Abstract class, should only be used through subclasses.
    A power system resource can be an item of equipment such as a switch, an equipment container containing many individual
    items of equipment such as a substation, or an organisational entity such as sub-control area. Power system resources
    can have measurements associated.
    """

    location: Optional[Location] = None
    """A `zepben.evolve.iec61968.common.location.Location` for this resource."""

    asset_info: Optional[AssetInfo] = None
    """A subclass of `zepben.evolve.iec61968.assets.asset_info.AssetInfo` providing information about the asset associated with this PowerSystemResource."""

