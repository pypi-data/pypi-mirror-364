# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from zepben.evolve import Organisation

from zepben.evolve.model.cim.iec61970.base.core.identified_object import IdentifiedObject

__all__ = ["OrganisationRole"]


class OrganisationRole(IdentifiedObject):
    """
    Identifies a way in which an organisation may participate in the utility enterprise (e.g., customer, manufacturer, etc).
    """

    organisation: Optional[Organisation] = None
    """The `zepben.evolve.cim.iec61968.common.organisation.Organisation` having this role."""
