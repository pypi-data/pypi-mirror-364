# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from zepben.evolve.database.sqlite.tables.column import Column, Nullable
from zepben.evolve.database.sqlite.tables.iec61970.base.core_tables import TableEquipment

__all__ = ["TableAuxiliaryEquipment", "TableFaultIndicators"]


class TableAuxiliaryEquipment(TableEquipment):
    terminal_mrid: Column = None

    def __init__(self):
        super(TableAuxiliaryEquipment, self).__init__()
        self.terminal_mrid = self._create_column("terminal_mrid", "TEXT", Nullable.NULL)


class TableFaultIndicators(TableAuxiliaryEquipment):

    def name(self) -> str:
        return "fault_indicators"
