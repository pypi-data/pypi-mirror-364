# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.
from __future__ import annotations

from typing import Optional

from zepben.evolve.model.cim.iec61968.assets.asset_info import AssetInfo

__all__ = ["ShuntCompensatorInfo"]


class ShuntCompensatorInfo(AssetInfo):
    """Properties of shunt capacitor, shunt reactor or switchable bank of shunt capacitor or reactor assets."""

    max_power_loss: Optional[int] = None
    """Maximum allowed apparent power loss in watts."""

    rated_current: Optional[int] = None
    """Rated current in amperes."""

    rated_reactive_power: Optional[int] = None
    """Rated reactive power in volt-amperes reactive."""

    rated_voltage: Optional[int] = None
    """Rated voltage in volts."""
