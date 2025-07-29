# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.
from typing import List

from zepben.evolve.database.sqlite.tables.column import Nullable, Column
from zepben.evolve.database.sqlite.tables.iec61970.base.core_tables import TableIdentifiedObjects
from zepben.evolve.database.sqlite.tables.iec61970.base.wires.container_tables import TableLines

__all__ = ["TableCircuits", "TableLoops"]


class TableCircuits(TableLines):
    loop_mrid: Column = None

    def __init__(self):
        super(TableCircuits, self).__init__()
        self.loop_mrid = self._create_column("loop_mrid", "TEXT", Nullable.NULL)

    def name(self) -> str:
        return "circuits"

    def non_unique_index_columns(self) -> List[List[Column]]:
        cols = super(TableCircuits, self).non_unique_index_columns()
        cols.append([self.loop_mrid])
        return cols


class TableLoops(TableIdentifiedObjects):
    def name(self) -> str:
        return "loops"
