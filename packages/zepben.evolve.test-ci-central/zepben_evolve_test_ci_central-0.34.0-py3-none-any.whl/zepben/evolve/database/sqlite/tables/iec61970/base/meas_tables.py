# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from typing import List

from zepben.evolve.database.sqlite.tables.column import Column, Nullable
from zepben.evolve.database.sqlite.tables.iec61970.base.core_tables import TableIdentifiedObjects

__all__ = ["TableMeasurements", "TableAnalogs", "TableControls", "TableAccumulators", "TableDiscretes", "TableIoPoints"]


class TableMeasurements(TableIdentifiedObjects):
    power_system_resource_mrid: Column = None
    remote_source_mrid: Column = None
    terminal_mrid: Column = None
    phases: Column = None
    unit_symbol: Column = None

    def __init__(self):
        super(TableMeasurements, self).__init__()
        self.power_system_resource_mrid = self._create_column("power_system_resource_mrid", "TEXT", Nullable.NULL)
        self.remote_source_mrid = self._create_column("remote_source_mrid", "TEXT", Nullable.NULL)
        self.terminal_mrid = self._create_column("terminal_mrid", "TEXT", Nullable.NULL)
        self.phases = self._create_column("phases", "TEXT", Nullable.NOT_NULL)
        self.unit_symbol = self._create_column("unit_symbol", "TEXT", Nullable.NOT_NULL)

    def non_unique_index_columns(self) -> List[List[Column]]:
        cols = super(TableMeasurements, self).non_unique_index_columns()
        cols.append([self.power_system_resource_mrid])
        cols.append([self.remote_source_mrid])
        cols.append([self.terminal_mrid])
        return cols


class TableAccumulators(TableMeasurements):

    def name(self) -> str:
        return "accumulators"


class TableAnalogs(TableMeasurements):
    positive_flow_in: Column = None

    def __init__(self):
        super(TableAnalogs, self).__init__()
        self.positive_flow_in = self._create_column("positive_flow_in", "BOOLEAN", Nullable.NOT_NULL)

    def name(self) -> str:
        return "analogs"


class TableIoPoints(TableIdentifiedObjects):
    pass


class TableControls(TableIoPoints):
    power_system_resource_mrid: Column = None

    def __init__(self):
        super(TableControls, self).__init__()
        self.power_system_resource_mrid = self._create_column("power_system_resource_mrid", "TEXT", Nullable.NULL)

    def name(self) -> str:
        return "controls"


class TableDiscretes(TableMeasurements):

    def name(self) -> str:
        return "discretes"
