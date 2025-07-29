# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from enum import Enum

__all__ = ["FeederDirection", "feeder_direction_from_value"]


class FeederDirection(Enum):
    NONE = 0
    UPSTREAM = 1
    DOWNSTREAM = 2
    BOTH = 3

    def has(self, other):
        """
        Check whether this Direction contains Direction other.
        `other` A `Direction` to compare against.
        Returns True if this is BOTH and other is not NONE, otherwise False
        """
        if self is FeederDirection.BOTH:
            return other is not FeederDirection.NONE
        else:
            return self is other

    def __add__(self, other):
        return FeederDirection(self.value | other.value)

    def __sub__(self, other):
        return FeederDirection(self.value - (self.value & other.value))

    @property
    def short_name(self):
        return str(self)[16:]


def feeder_direction_from_value(value: int) -> FeederDirection:
    if 0 <= value <= 3:
        return FeederDirection.NONE
    else:
        FeederDirection(value)
