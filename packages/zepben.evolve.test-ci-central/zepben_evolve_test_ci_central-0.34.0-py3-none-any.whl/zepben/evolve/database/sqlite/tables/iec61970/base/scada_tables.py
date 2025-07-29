# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from zepben.evolve.database.sqlite.tables.column import Column, Nullable
from zepben.evolve.database.sqlite.tables.iec61970.base.core_tables import TableIdentifiedObjects

__all__ = ["TableRemotePoints", "TableRemoteControls", "TableRemoteSources"]


class TableRemotePoints(TableIdentifiedObjects):
    pass


class TableRemoteControls(TableRemotePoints):
    control_mrid: Column = None

    def __init__(self):
        super(TableRemoteControls, self).__init__()
        self.control_mrid = self._create_column("control_mrid", "TEXT", Nullable.NULL)

    def name(self) -> str:
        return "remote_controls"


class TableRemoteSources(TableRemotePoints):
    measurement_mrid: Column = None

    def __init__(self):
        super(TableRemoteSources, self).__init__()
        self.measurement_mrid = self._create_column("measurement_mrid", "TEXT", Nullable.NULL)

    def name(self) -> str:
        return "remote_sources"
