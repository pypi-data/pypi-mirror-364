# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from typing import Optional

from zepben.evolve.model.cim.iec61970.base.meas.control import Control
from zepben.evolve.model.cim.iec61970.base.scada.remote_point import RemotePoint

__all__ = ["RemoteControl"]


class RemoteControl(RemotePoint):
    """
    Remote controls are outputs that are sent by the remote unit to actuators in the process.
    """

    control: Optional[Control] = None
    """The `zepben.evolve.iec61970.base.meas.control.Control` for the `RemoteControl` point."""
