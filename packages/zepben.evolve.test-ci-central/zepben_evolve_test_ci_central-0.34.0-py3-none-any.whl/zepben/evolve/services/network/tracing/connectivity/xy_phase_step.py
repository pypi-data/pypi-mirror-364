# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

__all__ = ["XyPhaseStep"]

from dataclassy import dataclass

from zepben.evolve import Terminal, PhaseCode


@dataclass(slots=True)
class XyPhaseStep(object):

    terminal: Terminal
    """
    The incoming terminal
    """

    phase_code: PhaseCode
    """
    The phases used to get to this step (should only be, XY, X or Y)
    """
