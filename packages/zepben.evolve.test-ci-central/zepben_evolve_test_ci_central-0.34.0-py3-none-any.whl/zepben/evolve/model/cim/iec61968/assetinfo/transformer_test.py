# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.
from typing import Optional

from zepben.evolve.model.cim.iec61970.base.core.identified_object import IdentifiedObject

__all__ = ["TransformerTest"]


class TransformerTest(IdentifiedObject):
    """
    Test result for transformer ends, such as short-circuit, open-circuit (excitation) or no-load test.
    """

    base_power: Optional[int] = None
    """
    Base power at which the tests are conducted, usually equal to the ratedS of one of the involved transformer ends in VA.
    """

    temperature: Optional[float] = None
    """
    Temperature at which the test is conducted in degrees Celsius.
    """
