from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import Field
from ..base import OmopClinicalModel


class Measurement(OmopClinicalModel):
    """
    The MEASUREMENT table contains records of Measurement, meaning systematic and
    standardized examination or testing of a particular physical property or condition
    based on an established standard.
    """

    measurement_id: int
    person_id: int
    measurement_concept_id: int
    measurement_date: date
    measurement_datetime: Optional[datetime] = None
    measurement_time: Optional[str] = Field(None, max_length=10)
    measurement_type_concept_id: int
    operator_concept_id: Optional[int] = None
    value_as_number: Optional[Decimal] = None
    value_as_concept_id: Optional[int] = None
    unit_concept_id: Optional[int] = None
    range_low: Optional[Decimal] = None
    range_high: Optional[Decimal] = None
    provider_id: Optional[int] = None
    visit_occurrence_id: Optional[int] = None
    visit_detail_id: Optional[int] = None
    measurement_source_value: Optional[str] = Field(None, max_length=50)
    measurement_source_concept_id: Optional[int] = None
    unit_source_value: Optional[str] = Field(None, max_length=50)
    value_source_value: Optional[str] = Field(None, max_length=50)
    # OMOP CDM 5.4 fields
    measurement_event_id: Optional[int] = None
    meas_event_field_concept_id: Optional[int] = None
