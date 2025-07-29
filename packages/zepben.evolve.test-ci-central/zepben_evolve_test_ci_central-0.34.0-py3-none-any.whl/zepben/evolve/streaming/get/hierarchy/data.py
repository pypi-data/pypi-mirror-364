# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.
from __future__ import annotations

from typing import Dict

from dataclassy import dataclass

__all__ = ["NetworkHierarchy"]

from zepben.evolve import Circuit, Feeder, GeographicalRegion, Loop, SubGeographicalRegion, Substation


@dataclass(slots=True)
class NetworkHierarchy(object):
    """Container for simplified network hierarchy objects"""
    geographical_regions: Dict[str, GeographicalRegion]
    sub_geographical_regions: Dict[str, SubGeographicalRegion]
    substations: Dict[str, Substation]
    feeders: Dict[str, Feeder]
    circuits: Dict[str, Circuit]
    loops: Dict[str, Loop]
