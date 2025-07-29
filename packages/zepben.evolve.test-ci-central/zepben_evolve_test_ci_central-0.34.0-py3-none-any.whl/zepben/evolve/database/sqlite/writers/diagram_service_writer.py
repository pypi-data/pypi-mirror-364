# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from zepben.evolve import DiagramObject, Diagram, DiagramService
from zepben.evolve.database.sqlite.writers.base_service_writer import BaseServiceWriter
from zepben.evolve.database.sqlite.writers.diagram_cim_writer import DiagramCIMWriter

__all__ = ["DiagramServiceWriter"]


class DiagramServiceWriter(BaseServiceWriter):

    def save(self, service: DiagramService, writer: DiagramCIMWriter) -> bool:
        status = super(DiagramServiceWriter, self).save(service, writer)

        for obj in service.objects(DiagramObject):
            status = status and self.validate_save(obj, writer.save_diagram_object)
        for obj in service.objects(Diagram):
            status = status and self.validate_save(obj, writer.save_diagram)

        return status
