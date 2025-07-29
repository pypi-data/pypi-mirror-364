# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.
from sqlite3 import Cursor

from dataclassy import dataclass

from zepben.evolve import DatabaseTables, DataSource, TableMetadataDataSources
from zepben.evolve.database.sqlite.writers.utils import try_execute_single_update

__all__ = ["MetadataEntryWriter"]


@dataclass(slots=True)
class MetadataEntryWriter(object):
    database_tables: DatabaseTables
    cursor: Cursor

    def save(self, data_source: DataSource) -> bool:
        table = self.database_tables.get_table(TableMetadataDataSources)
        insert = self.database_tables.get_insert(TableMetadataDataSources)

        insert.add_value(table.source.query_index, data_source.source)
        insert.add_value(table.version.query_index, data_source.version)
        # TODO: JVM seems to use Z as TZ offset (for UTC+0?) while python uses +HH:mm format. Need to investigate here
        insert.add_value(table.timestamp.query_index, f"{data_source.timestamp.isoformat()}Z")

        return try_execute_single_update(insert, self.cursor, "data source")
