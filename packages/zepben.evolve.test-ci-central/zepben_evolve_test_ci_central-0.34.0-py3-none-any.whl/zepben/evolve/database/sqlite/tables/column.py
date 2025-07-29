# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.
from enum import Enum

from dataclassy import dataclass

from zepben.evolve.util import require


class Nullable(Enum):
    NONE = ""
    NOT_NULL = "NOT NULL"
    NULL = "NULL"

    @property
    def sql(self):
        return self.value


@dataclass(slots=True)
class Column:
    query_index: int
    name: str
    type: str
    nullable: Nullable = Nullable.NONE

    def __init__(self):
        require(self.query_index >= 0, lambda: "You cannot use a negative query index.")
        require(not self.name.isspace() and self.name, lambda: "Column Name cannot be blank.")
        require(not self.type.isspace() and self.type, lambda: "Column Type cannot be blank.")

    def __str__(self):
        return f"{self.name} {self.type} {self.nullable.sql}".rstrip()
