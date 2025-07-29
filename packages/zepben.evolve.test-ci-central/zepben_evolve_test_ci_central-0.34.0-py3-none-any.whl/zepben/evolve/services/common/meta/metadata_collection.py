# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.
from typing import List, Generator

from dataclassy import dataclass

from zepben.evolve import DataSource

__all__ = ["MetadataCollection"]


@dataclass(slots=True)
class MetadataCollection(object):
    _data_sources: List[DataSource] = list()

    @property
    def data_sources(self) -> Generator[DataSource, None, None]:
        for source in self._data_sources:
            yield source

    def num_sources(self) -> int:
        return len(self._data_sources)

    def add(self, data_source: DataSource):
        self._data_sources.append(data_source)

