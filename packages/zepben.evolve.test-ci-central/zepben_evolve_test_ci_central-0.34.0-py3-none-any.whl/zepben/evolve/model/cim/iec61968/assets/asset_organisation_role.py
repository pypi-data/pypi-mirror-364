# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from zepben.evolve.model.cim.iec61968.common.organisation_role import OrganisationRole

__all__ = ["AssetOrganisationRole", "AssetOwner"]


class AssetOrganisationRole(OrganisationRole):
    """ Role an organisation plays with respect to asset. """
    pass


class AssetOwner(AssetOrganisationRole):
    """ Owner of the Asset """
    pass

