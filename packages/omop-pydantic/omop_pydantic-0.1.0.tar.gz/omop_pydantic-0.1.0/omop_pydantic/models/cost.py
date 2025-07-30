from decimal import Decimal
from typing import Optional

from pydantic import Field
from ..base import OmopReferenceModel


class Cost(OmopReferenceModel):
    """
    OMOP CDM Cost table model.

    The COST table captures records containing the cost of any medical entity recorded
    in one of the OMOP clinical event tables such as DRUG_EXPOSURE, PROCEDURE_OCCURRENCE,
    VISIT_OCCURRENCE, VISIT_DETAIL, DEVICE_EXPOSURE, OBSERVATION or MEASUREMENT.
    """

    cost_id: int
    cost_event_id: int
    cost_domain_id: str = Field(max_length=20)
    cost_type_concept_id: int
    currency_concept_id: Optional[int] = None
    total_charge: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    total_paid: Optional[Decimal] = None
    paid_by_payer: Optional[Decimal] = None
    paid_by_patient: Optional[Decimal] = None
    paid_patient_copay: Optional[Decimal] = None
    paid_patient_coinsurance: Optional[Decimal] = None
    paid_patient_deductible: Optional[Decimal] = None
    paid_by_primary: Optional[Decimal] = None
    paid_ingredient_cost: Optional[Decimal] = None
    paid_dispensing_fee: Optional[Decimal] = None
    payer_plan_period_id: Optional[int] = None
    amount_allowed: Optional[Decimal] = None
    revenue_code_concept_id: Optional[int] = None
    revenue_code_source_value: Optional[str] = Field(default=None, max_length=50)
    drg_concept_id: Optional[int] = None
    drg_source_value: Optional[str] = Field(default=None, max_length=3)
