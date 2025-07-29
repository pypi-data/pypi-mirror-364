# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from dataclassy import dataclass

if TYPE_CHECKING:
    from zepben.evolve.model.cim.iec61970.base.core.identified_object import IdentifiedObject
    from zepben.evolve.model.cim.iec61970.base.core.name_type import NameType

__all__ = ["Name"]


@dataclass(slots=True)
class Name:
    """
    The Name class provides the means to define any number of human readable names for an object. A name is **not** to be used for defining inter-object
    relationships. For inter-object relationships instead use the object identification 'mRID'.
    """

    name: str
    """Any free text that name the object."""

    type: NameType
    """Type of this name."""

    identified_object: Optional[IdentifiedObject] = None
    """Identified object that this name designates."""
