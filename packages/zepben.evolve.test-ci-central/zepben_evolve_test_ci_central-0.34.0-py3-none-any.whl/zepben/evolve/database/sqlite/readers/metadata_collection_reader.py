# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from zepben.evolve import BaseServiceReader, MetadataEntryReader, TableMetadataDataSources

__all__ = ["MetadataCollectionReader"]


class MetadataCollectionReader(BaseServiceReader):
    """
    Class for reading the [MetadataCollection] from the database.
    """

    def load(self, reader: MetadataEntryReader) -> bool:
        status = True

        status = status and self._load_each(TableMetadataDataSources, "metadata data sources", reader.load_metadata)

        return status
