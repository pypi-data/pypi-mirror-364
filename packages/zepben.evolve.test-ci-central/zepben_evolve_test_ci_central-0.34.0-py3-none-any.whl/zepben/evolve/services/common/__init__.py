# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from zepben.protobuf.cim.iec61968.common.Document_pb2 import Document as PBDocument
from zepben.protobuf.cim.iec61968.common.OrganisationRole_pb2 import OrganisationRole as PBOrganisationRole
from zepben.protobuf.cim.iec61968.common.Organisation_pb2 import Organisation as PBOrganisation
from zepben.protobuf.cim.iec61970.base.core.IdentifiedObject_pb2 import IdentifiedObject as PBIdentifiedObject


PBOrganisationRole.mrid = lambda self: self.io.mRID
PBDocument.mrid = lambda self: self.io.mRID
PBOrganisation.mrid = lambda self: self.io.mRID
PBIdentifiedObject.name_and_mrid = lambda self: f"{self.mRID}{f' [{self.name}]' if self.name else ''}"
PBDocument.name_and_mrid = lambda self: self.io.name_and_mrid()


