# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from datetime import datetime

from dataclassy import dataclass

__all__ = ["DataSource"]


@dataclass(slots=True)
class DataSource(object):
    source: str
    version: str
    timestamp: datetime = datetime.now()
