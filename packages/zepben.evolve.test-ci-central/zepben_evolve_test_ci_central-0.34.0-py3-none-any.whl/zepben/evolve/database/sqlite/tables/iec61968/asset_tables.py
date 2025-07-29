# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from zepben.evolve.database.sqlite.tables.column import Column, Nullable
from zepben.evolve.database.sqlite.tables.iec61968.common_tables import TableOrganisationRoles
from zepben.evolve.database.sqlite.tables.iec61970.base.core_tables import TableIdentifiedObjects

__all__ = ["TableAssets", "TableAssetContainers", "TableAssetInfo", "TableAssetOrganisationRoles", "TableAssetOwners", "TableStructures", "TableStreetlights",
           "TablePoles"]


class TableAssets(TableIdentifiedObjects):
    location_mrid: Column = None

    def __init__(self):
        super(TableAssets, self).__init__()
        self.location_mrid = self._create_column("location_mrid", "TEXT", Nullable.NULL)


class TableAssetContainers(TableAssets):
    pass


class TableAssetInfo(TableIdentifiedObjects):
    pass


class TableAssetOrganisationRoles(TableOrganisationRoles):
    pass


class TableAssetOwners(TableAssetOrganisationRoles):

    def name(self) -> str:
        return "asset_owners"


class TableStructures(TableAssetContainers):
    pass


class TablePoles(TableStructures):
    classification: Column = None

    def __init__(self):
        super(TablePoles, self).__init__()
        self.classification = self._create_column("classification", "TEXT", Nullable.NOT_NULL)

    def name(self) -> str:
        return "poles"


class TableStreetlights(TableAssets):
    pole_mrid: Column = None
    lamp_kind: Column = None
    light_rating: Column = None

    def __init__(self):
        super(TableStreetlights, self).__init__()
        self.pole_mrid = self._create_column("pole_mrid", "TEXT", Nullable.NULL)
        self.lamp_kind = self._create_column("lamp_kind", "TEXT", Nullable.NOT_NULL)
        self.light_rating = self._create_column("light_rating", "INTEGER", Nullable.NULL)

    def name(self) -> str:
        return "streetlights"
