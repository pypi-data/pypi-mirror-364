# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from zepben.protobuf.cim.iec61970.base.meas.MeasurementValue_pb2 import MeasurementValue as PBMeasurementValue
from zepben.protobuf.cim.iec61970.base.meas.AccumulatorValue_pb2 import AccumulatorValue as PBAccumulatorValue
from zepben.protobuf.cim.iec61970.base.meas.AnalogValue_pb2 import AnalogValue as PBAnalogValue
from zepben.protobuf.cim.iec61970.base.meas.DiscreteValue_pb2 import DiscreteValue as PBDiscreteValue
from zepben.evolve.model.cim.iec61970.base.meas.value import AnalogValue, AccumulatorValue, DiscreteValue, MeasurementValue

from zepben.evolve.services.measurement.measurements import MeasurementService

__all__ = ["measurementvalue_to_cim", "analogvalue_to_cim", "accumulatorvalue_to_cim", "discretevalue_to_cim"]


def measurementvalue_to_cim(pb: PBMeasurementValue, cim: MeasurementValue):
    cim.time_stamp = pb.timeStamp.ToDatetime()


def analogvalue_to_cim(pb: PBAnalogValue, service: MeasurementService):
    cim = AnalogValue(analog_mrid=pb.analogMRID, value=pb.value)
    measurementvalue_to_cim(pb.mv, cim)
    service.add(cim)


def accumulatorvalue_to_cim(pb: PBAccumulatorValue, service: MeasurementService):
    cim = AccumulatorValue(accumulator_mrid=pb.accumulatorMRID, value=pb.value)
    measurementvalue_to_cim(pb.mv, cim)
    service.add(cim)


def discretevalue_to_cim(pb: PBDiscreteValue, service: MeasurementService):
    cim = DiscreteValue(discrete_mrid=pb.discreteMRID, value=pb.value)
    measurementvalue_to_cim(pb.mv, cim)
    service.add(cim)


PBAccumulatorValue.to_cim = accumulatorvalue_to_cim
PBAnalogValue.to_cim = analogvalue_to_cim
PBDiscreteValue.to_cim = discretevalue_to_cim
PBMeasurementValue.to_cim = measurementvalue_to_cim