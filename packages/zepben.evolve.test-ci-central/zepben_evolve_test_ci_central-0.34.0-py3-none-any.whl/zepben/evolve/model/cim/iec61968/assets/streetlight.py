# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from __future__ import annotations

from enum import Enum
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from zepben.evolve import Pole

from zepben.evolve.model.cim.iec61968.assets.asset import Asset

__all__ = ["Streetlight", "StreetlightLampKind"]


class StreetlightLampKind(Enum):
    """
    Kind of lamp for a `Streetlight`
    """

    UNKNOWN = 0
    HIGH_PRESSURE_SODIUM = 1
    MERCURY_VAPOR = 2
    METAL_HALIDE = 3
    OTHER = 4

    @property
    def short_name(self):
        return str(self)[20:]


class Streetlight(Asset):
    """
    A Streetlight asset.
    """

    pole: Optional[Pole] = None
    """The `zepben.evolve.cim.iec61968.assets.pole.Pole` this Streetlight is attached to."""

    light_rating: Optional[int] = None
    """The power rating of the light in watts."""

    lamp_kind: StreetlightLampKind = StreetlightLampKind.UNKNOWN
    """The kind of lamp."""
