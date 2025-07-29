# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from __future__ import annotations

from zepben.evolve.model.cim.iec61970.base.core.power_system_resource import PowerSystemResource

__all__ = ["ConnectivityNodeContainer"]


class ConnectivityNodeContainer(PowerSystemResource):
    """
    A base class for all objects that may contain connectivity nodes or topological nodes.
    """
    pass
