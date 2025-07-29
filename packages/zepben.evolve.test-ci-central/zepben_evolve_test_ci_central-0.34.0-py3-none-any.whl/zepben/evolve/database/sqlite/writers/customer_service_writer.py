# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.

from zepben.evolve import CustomerCIMWriter, Organisation, Customer, CustomerAgreement, PricingStructure, Tariff, CustomerService
from zepben.evolve.database.sqlite.writers.base_service_writer import BaseServiceWriter

__all__ = ["CustomerServiceWriter"]


class CustomerServiceWriter(BaseServiceWriter):

    def save(self, service: CustomerService, writer: CustomerCIMWriter) -> bool:
        status = super(CustomerServiceWriter, self).save(service, writer)

        for obj in service.objects(Organisation):
            status = status and self.try_save_common(obj, writer.save_organisation)
        for obj in service.objects(Customer):
            status = status and self.validate_save(obj, writer.save_customer)
        for obj in service.objects(CustomerAgreement):
            status = status and self.validate_save(obj, writer.save_customer_agreement)
        for obj in service.objects(PricingStructure):
            status = status and self.validate_save(obj, writer.save_pricing_structure)
        for obj in service.objects(Tariff):
            status = status and self.validate_save(obj, writer.save_tariff)

        return status
