# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from __future__ import annotations

from zepben.evolve.model.cim.iec61968.common.document import Document

__all__ = ["Tariff"]


class Tariff(Document):
    """
    Document, approved by the responsible regulatory agency, listing the terms and conditions,
    including a schedule of prices, under which utility services will be provided. It has a
    unique number within the state or province. For rate schedules it is frequently allocated
    by the affiliated Public utilities commission (PUC).
    """
    pass
