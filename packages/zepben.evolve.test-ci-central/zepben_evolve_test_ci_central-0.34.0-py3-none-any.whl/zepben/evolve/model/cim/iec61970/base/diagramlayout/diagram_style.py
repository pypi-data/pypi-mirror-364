# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.



from enum import Enum

__all__ = ["DiagramStyle"]


class DiagramStyle(Enum):
    """
    The diagram style refer to a style used by the originating system for a diagram.  A diagram style describes
    information such as schematic, geographic, bus-branch etc.
    """

    SCHEMATIC = 0
    """The diagram should be styled as a schematic view."""

    GEOGRAPHIC = 1
    """The diagram should be styled as a geographic view."""

    @property
    def short_name(self):
        return str(self)[13:]
