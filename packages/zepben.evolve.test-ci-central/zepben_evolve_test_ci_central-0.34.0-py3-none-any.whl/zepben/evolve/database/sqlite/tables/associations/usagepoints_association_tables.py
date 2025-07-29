# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from typing import List

from zepben.evolve.database.sqlite.tables.column import Column, Nullable
from zepben.evolve.database.sqlite.tables.sqlite_table import SqliteTable

__all__ = ["TableUsagePointsEndDevices"]


class TableUsagePointsEndDevices(SqliteTable):
    usage_point_mrid: Column = None
    end_device_mrid: Column = None

    def __init__(self):
        super(TableUsagePointsEndDevices, self).__init__()
        self.usage_point_mrid = self._create_column("usage_point_mrid", "TEXT", Nullable.NOT_NULL)
        self.end_device_mrid = self._create_column("end_device_mrid", "TEXT", Nullable.NOT_NULL)

    def name(self) -> str:
        return "usage_points_end_devices"

    def unique_index_columns(self) -> List[List[Column]]:
        cols = super(TableUsagePointsEndDevices, self).unique_index_columns()
        cols.append([self.usage_point_mrid, self.end_device_mrid])
        return cols

    def non_unique_index_columns(self) -> List[List[Column]]:
        cols = super(TableUsagePointsEndDevices, self).non_unique_index_columns()
        cols.append([self.usage_point_mrid])
        cols.append([self.end_device_mrid])
        return cols

