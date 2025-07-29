# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.



from enum import Enum

__all__ = ["TransformerFunctionKind"]


class TransformerFunctionKind(Enum):
    other = 0
    """ Another type of transformer. """

    voltageRegulator = 1
    """ A transformer that changes the voltage magnitude at a certain point in the power system. """

    distributionTransformer = 2
    """ A transformer that provides the final voltage transformation in the electric power distribution system. """

    isolationTransformer = 3
    """ A transformer whose primary purpose is to isolate circuits. """

    autotransformer = 4
    """ A transformer with a special winding divided into several sections enabling the voltage to be varied at will. (IEC ref 811-26-04). """

    powerTransformer = 5
    """"""

    secondaryTransformer = 6
    """"""

    @property
    def short_name(self):
        return str(self)[24:]
