# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from zepben.evolve.database.sqlite.tables.column import Column, Nullable
from zepben.evolve.database.sqlite.tables.iec61970.base.core_tables import TableConductingEquipment

__all__ = ["TableConductors", "TableAcLineSegments"]


class TableConductors(TableConductingEquipment):
    length: Column = None
    wire_info_mrid: Column = None

    def __init__(self):
        super(TableConductors, self).__init__()
        self.length = self._create_column("length", "NUMBER", Nullable.NULL)
        self.wire_info_mrid = self._create_column("wire_info_mrid", "TEXT", Nullable.NULL)


class TableAcLineSegments(TableConductors):
    per_length_sequence_impedance_mrid: Column = None

    def __init__(self):
        super(TableAcLineSegments, self).__init__()
        self.per_length_sequence_impedance_mrid = self._create_column("per_length_sequence_impedance_mrid", "TEXT", Nullable.NULL)

    def name(self) -> str:
        return "ac_line_segments"
