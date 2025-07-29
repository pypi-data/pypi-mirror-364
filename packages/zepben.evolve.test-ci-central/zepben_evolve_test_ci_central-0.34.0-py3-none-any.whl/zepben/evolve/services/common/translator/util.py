# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.
from typing import Optional

from zepben.protobuf.cim.iec61970.base.core.IdentifiedObject_pb2 import IdentifiedObject as PBIdentifiedObject

__all__ = [
    "mrid_or_empty", "int_or_none", "uint_or_none", "float_or_none", "long_or_none", "str_or_none", "from_nullable_int", "from_nullable_uint",
    "from_nullable_float", "from_nullable_long"
]


_UNKNOWN_FLOAT = float("-inf")
_UNKNOWN_INT = -2147483648
_UNKNOWN_UINT = 4294967295
_UNKNOWN_LONG = -9223372036854775808


def mrid_or_empty(io: PBIdentifiedObject) -> str:
    return str(io.mrid) if io else ""


def int_or_none(value: int) -> Optional[int]:
    return value if value != _UNKNOWN_INT else None


def uint_or_none(value: int) -> Optional[int]:
    return value if value != _UNKNOWN_UINT else None


def float_or_none(value: float) -> Optional[float]:
    return value if value != _UNKNOWN_FLOAT else None


def long_or_none(value: int) -> Optional[int]:
    return value if value != _UNKNOWN_LONG else None


def str_or_none(value: str) -> Optional[str]:
    return value if value else None


def from_nullable_int(value: Optional[int]) -> int:
    return value if value is not None else _UNKNOWN_INT


def from_nullable_uint(value: Optional[int]) -> int:
    return value if value is not None else _UNKNOWN_UINT


def from_nullable_float(value: Optional[float]) -> float:
    return value if value is not None else _UNKNOWN_FLOAT


def from_nullable_long(value: Optional[int]) -> int:
    return value if value is not None else _UNKNOWN_LONG
