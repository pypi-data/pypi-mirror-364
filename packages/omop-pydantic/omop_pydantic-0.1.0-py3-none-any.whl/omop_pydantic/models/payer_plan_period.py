from datetime import date
from typing import Optional

from pydantic import Field
from ..base import OmopClinicalModel


class PayerPlanPeriod(OmopClinicalModel):
    """
    OMOP CDM PAYER_PLAN_PERIOD table.

    This table captures details of the period of time that a Person is continuously enrolled under a specific health Plan benefit structure from a given Payer. Each Person receiving healthcare is typically covered by a health benefit plan, which pays for (fully or partially) the care. These benefit plans are administered by a payer, such as an health insurer or an employer. In each plan the details of the health benefits are defined for the Person or her family, and the health benefit Plan might change over time typically with increasing utilization (reaching certain cost thresholds such as deductibles), plan availability and purchasing choices of the Person. The unique combinations of Payer organizations, health benefit Plans and time periods in which they are valid for a Person are recorded in this table.
    """

    payer_plan_period_id: int
    person_id: int
    payer_plan_period_start_date: date
    payer_plan_period_end_date: date
    payer_concept_id: Optional[int] = None
    payer_source_value: Optional[str] = Field(None, max_length=50)
    payer_source_concept_id: Optional[int] = None
    plan_concept_id: Optional[int] = None
    plan_source_value: Optional[str] = Field(None, max_length=50)
    plan_source_concept_id: Optional[int] = None
    sponsor_concept_id: Optional[int] = None
    sponsor_source_value: Optional[str] = Field(None, max_length=50)
    sponsor_source_concept_id: Optional[int] = None
    family_source_value: Optional[str] = Field(None, max_length=50)
    stop_reason_concept_id: Optional[int] = None
    stop_reason_source_value: Optional[str] = Field(None, max_length=50)
    stop_reason_source_concept_id: Optional[int] = None
