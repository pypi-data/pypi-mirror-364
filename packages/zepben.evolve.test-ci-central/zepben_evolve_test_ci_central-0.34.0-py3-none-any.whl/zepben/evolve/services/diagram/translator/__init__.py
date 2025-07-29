# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from zepben.protobuf.cim.iec61970.base.diagramlayout.DiagramObject_pb2 import DiagramObject
from zepben.protobuf.cim.iec61970.base.diagramlayout.Diagram_pb2 import Diagram


Diagram.mrid = lambda self: self.io.mRID
DiagramObject.mrid = lambda self: self.io.mRID
