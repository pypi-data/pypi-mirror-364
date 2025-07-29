# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.
from enum import Enum

__all__ = ["BatteryStateKind"]


class BatteryStateKind(Enum):
    """Battery state"""
    
    UNKNOWN = 0
    """Battery state is not known."""

    discharging = 1
    """Stored energy is decreasing."""

    full = 2
    """Unable to charge, and not discharging."""

    waiting = 3
    """Neither charging nor discharging, but able to do so."""

    charging = 4
    """Stored energy is increasing."""

    empty = 5
    """Unable to discharge, and not charging."""

    @property
    def short_name(self):
        return str(self)[17:]
