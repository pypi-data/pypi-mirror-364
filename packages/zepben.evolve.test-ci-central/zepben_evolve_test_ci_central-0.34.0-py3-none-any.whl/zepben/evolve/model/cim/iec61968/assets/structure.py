# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from __future__ import annotations

from zepben.evolve.model.cim.iec61968.assets.asset import AssetContainer

__all__ = ["Structure"]


class Structure(AssetContainer):
    """
    Construction holding assets such as conductors, transformers, switchgear, etc. Where applicable, number of conductors
    can be derived from the number of associated wire spacing instances.
    """
    pass
