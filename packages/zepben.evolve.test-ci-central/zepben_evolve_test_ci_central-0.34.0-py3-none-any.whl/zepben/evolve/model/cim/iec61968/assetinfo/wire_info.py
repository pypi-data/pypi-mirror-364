# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from __future__ import annotations

from typing import Optional

from zepben.evolve.model.cim.iec61968.assetinfo.wire_material_kind import WireMaterialKind
from zepben.evolve.model.cim.iec61968.assets.asset_info import AssetInfo

__all__ = ["WireInfo", "CableInfo", "OverheadWireInfo"]


class WireInfo(AssetInfo):
    """
    Wire data that can be specified per line segment phase, or for the line segment as a whole in case its phases all
    have the same wire characteristics

    Attributes -
        rated_current : Current carrying capacity of the wire under stated thermal conditions in amperes.
        material : `zepben.protobuf.cim.iec61968.assetinfo.WireMaterialKind` - Conductor material.
    """
    rated_current: Optional[int] = None
    material: WireMaterialKind = WireMaterialKind.UNKNOWN


class CableInfo(WireInfo):
    """
    Cable data. A cable is an underground conductor.
    """
    pass


class OverheadWireInfo(WireInfo):
    """
    Overhead wire data. A "wire" is an above ground conductor.
    """
    pass

