from datetime import datetime, date
from typing import Optional
from pydantic import Field

from ..base import OmopClinicalModel


class ConditionOccurrence(OmopClinicalModel):
    """
    OMOP CDM CONDITION_OCCURRENCE table.

    This table contains records of patient conditions diagnosed or reported during
    healthcare encounters, including diseases, disorders, injuries, and other
    health conditions.
    """

    condition_occurrence_id: int
    person_id: int
    condition_concept_id: int
    condition_start_date: date
    condition_start_datetime: Optional[datetime] = None
    condition_end_date: Optional[date] = None
    condition_end_datetime: Optional[datetime] = None
    condition_type_concept_id: int
    condition_status_concept_id: Optional[int] = None
    stop_reason: Optional[str] = Field(None, max_length=20)
    provider_id: Optional[int] = None
    visit_occurrence_id: Optional[int] = None
    visit_detail_id: Optional[int] = None
    condition_source_value: Optional[str] = Field(None, max_length=50)
    condition_source_concept_id: Optional[int] = None
    condition_status_source_value: Optional[str] = Field(None, max_length=50)
