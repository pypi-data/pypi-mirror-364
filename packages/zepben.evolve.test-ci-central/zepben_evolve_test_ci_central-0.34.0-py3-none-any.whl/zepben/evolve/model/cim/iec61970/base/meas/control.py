# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from zepben.evolve import RemoteControl

from zepben.evolve.model.cim.iec61970.base.meas.iopoint import IoPoint

__all__ = ["Control"]


class Control(IoPoint):
    """
    Control is used for supervisory/device control. It represents control outputs that are used to change the state in a
    process, e.g. close or open breaker, a set point value or a raise lower command.
    """

    power_system_resource_mrid: Optional[str] = None
    """AnalogValue represents an analog MeasurementValue."""
    
    remote_control: Optional[RemoteControl] = None
    """AnalogValue represents an analog MeasurementValue."""
