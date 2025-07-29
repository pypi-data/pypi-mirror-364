# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from zepben.evolve.database.sqlite.tables.iec61968.common_tables import TableDocuments

__all__ = ["TableOperationalRestrictions"]


class TableOperationalRestrictions(TableDocuments):

    def name(self):
        return "operational_restrictions"
