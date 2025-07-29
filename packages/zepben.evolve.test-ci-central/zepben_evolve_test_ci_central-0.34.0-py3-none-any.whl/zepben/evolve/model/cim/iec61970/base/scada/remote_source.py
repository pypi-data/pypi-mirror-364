# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from typing import Optional

from zepben.evolve.model.cim.iec61970.base.meas.measurement import Measurement
from zepben.evolve.model.cim.iec61970.base.scada.remote_point import RemotePoint

__all__ = ["RemoteSource"]


class RemoteSource(RemotePoint):
    """
    Remote sources are state variables that are telemetered or calculated within the remote unit.
    """

    measurement: Optional[Measurement] = None
    """The `meas.measurement.Measurement` for the `RemoteSource` point."""
