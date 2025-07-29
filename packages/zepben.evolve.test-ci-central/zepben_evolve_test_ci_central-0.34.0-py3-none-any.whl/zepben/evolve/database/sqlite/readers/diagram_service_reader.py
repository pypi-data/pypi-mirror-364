# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.
from zepben.evolve import BaseServiceReader, TableDiagrams, TableDiagramObjects, TableDiagramObjectPoints, DiagramCIMReader

__all__ = ["DiagramServiceReader"]


class DiagramServiceReader(BaseServiceReader):
    """
    Class for reading a `DiagramService` from the database.
    """

    def load(self, reader: DiagramCIMReader) -> bool:
        status = self.load_name_types(reader)

        status = status and self._load_each(TableDiagrams, "diagrams", reader.load_diagram)
        status = status and self._load_each(TableDiagramObjects, "diagram objects", reader.load_diagram_object)
        status = status and self._load_each(TableDiagramObjectPoints, "diagram object points", reader.load_diagram_object_point)

        status = status and self.load_names(reader)

        return status
