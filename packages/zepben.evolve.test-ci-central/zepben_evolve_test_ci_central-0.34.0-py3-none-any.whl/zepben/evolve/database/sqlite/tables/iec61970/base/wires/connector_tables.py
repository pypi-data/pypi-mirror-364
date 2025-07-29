# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from zepben.evolve.database.sqlite.tables.iec61970.base.core_tables import TableConductingEquipment

__all__ = ["TableConnectors", "TableBusbarSections", "TableJunctions"]


class TableConnectors(TableConductingEquipment):
    pass


class TableBusbarSections(TableConnectors):
    def name(self) -> str:
        return "busbar_sections"


class TableJunctions(TableConnectors):
    def name(self) -> str:
        return "junctions"
