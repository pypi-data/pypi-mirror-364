# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.
from dataclasses import dataclass, field
from typing import Optional, Any, List, Dict, TypeVar

from zepben.evolve import IdentifiedObject

T = TypeVar("T")


@dataclass()
class Difference:
    pass


@dataclass()
class ValueDifference(Difference):
    source_value: Optional[Any]
    target_value: Optional[Any]


@dataclass()
class CollectionDifference(Difference):
    missing_from_target: List[Any] = field(default_factory=list)
    missing_from_source: List[Any] = field(default_factory=list)
    modifications: List[Difference] = field(default_factory=list)


@dataclass()
class ObjectDifference(Difference):
    source: T
    target: T
    differences: Dict[str, Difference] = field(default_factory=dict)


@dataclass()
class ReferenceDifference(Difference):
    source: Optional[IdentifiedObject]
    target_value: Optional[IdentifiedObject]


@dataclass()
class IndexedDifference(Difference):
    index: int
    difference: Difference
