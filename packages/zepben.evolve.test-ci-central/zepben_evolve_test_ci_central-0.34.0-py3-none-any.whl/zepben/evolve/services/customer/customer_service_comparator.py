# Copyright (c) Zeppelin Bend Pty Ltd (Zepben) 2025 - All Rights Reserved.
# Unauthorized use, copy, or distribution of this file or its contents, via any medium is strictly prohibited.
from zepben.evolve import BaseServiceComparator, ObjectDifference, Customer, CustomerAgreement, PricingStructure, Tariff


class CustomerServiceComparator(BaseServiceComparator):
    """
    Compare the objects supported by the customer service.
    """

    def _compare_agreement(self, diff: ObjectDifference) -> ObjectDifference:
        return self._compare_document(diff)

    def _compare_customer(self, source: Customer, target: Customer) -> ObjectDifference:
        diff = ObjectDifference(source, target)

        self._compare_values(diff, Customer.kind)
        self._compare_id_reference_collections(diff, Customer.agreements)

        return self._compare_organisation_role(diff)

    def _compare_customer_agreement(self, source: CustomerAgreement, target: CustomerAgreement) -> ObjectDifference:
        diff = ObjectDifference(source, target)

        self._compare_id_references(diff, CustomerAgreement.customer)
        self._compare_id_reference_collections(diff, CustomerAgreement.pricing_structures)

        return self._compare_agreement(diff)

    def _compare_pricing_structure(self, source: PricingStructure, target: PricingStructure) -> ObjectDifference:
        diff = ObjectDifference(source, target)

        self._compare_id_reference_collections(diff, PricingStructure.tariffs)

        return self._compare_document(diff)

    def _compare_tariff(self, source: Tariff, target: Tariff) -> ObjectDifference:
        return self._compare_document(ObjectDifference(source, target))
