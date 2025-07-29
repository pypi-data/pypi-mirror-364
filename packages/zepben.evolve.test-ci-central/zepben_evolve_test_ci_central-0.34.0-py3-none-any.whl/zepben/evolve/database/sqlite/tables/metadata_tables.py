# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from zepben.evolve.database.sqlite.tables.column import Column, Nullable
from zepben.evolve.database.sqlite.tables.sqlite_table import SqliteTable

__all__ = ["TableVersion", "TableMetadataDataSources"]


class TableVersion(SqliteTable):
    version: Column = None

    SUPPORTED_VERSION = 42

    def __init__(self):
        self.version = self._create_column("version", "TEXT", Nullable.NOT_NULL)

    def name(self) -> str:
        return "version"


class TableMetadataDataSources(SqliteTable):
    source: Column = None
    version: Column = None
    timestamp: Column = None

    def __init__(self):
        self.source = self._create_column("source", "TEXT", Nullable.NOT_NULL)
        self.version = self._create_column("version", "TEXT", Nullable.NOT_NULL)
        self.timestamp = self._create_column("timestamp", "TEXT", Nullable.NOT_NULL)

    def name(self) -> str:
        return "metadata_data_sources"
