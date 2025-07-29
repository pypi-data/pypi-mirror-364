# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.
import logging

from zepben.evolve import MetadataCollection, MetadataEntryWriter
from zepben.evolve.database.sqlite.writers.utils import validate_save

logger = logging.getLogger("metadata_entry_writer")

__all__ = ["MetadataCollectionWriter"]


class MetadataCollectionWriter(object):

    @staticmethod
    def save(metadata_collection: MetadataCollection, writer: MetadataEntryWriter) -> bool:
        status = True

        for data_source in metadata_collection.data_sources:
            status = status and validate_save(data_source, writer.save, lambda e: logger.error(f"Failed to save DataSource '{data_source.source}': {e}"))

        return status
