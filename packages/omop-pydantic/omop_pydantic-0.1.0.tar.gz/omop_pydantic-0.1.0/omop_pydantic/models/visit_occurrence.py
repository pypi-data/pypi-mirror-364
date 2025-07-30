from datetime import date, datetime
from typing import Optional

from pydantic import Field
from ..base import OmopClinicalModel


class VisitOccurrence(OmopClinicalModel):
    """
    The VISIT_OCCURRENCE table contains the spans of time a Person continuously receives medical services
    from one or more providers at a Care Site in a given setting within the health care system.
    """

    visit_occurrence_id: int
    person_id: int
    visit_concept_id: int
    visit_start_date: date
    visit_start_datetime: Optional[datetime] = None
    visit_end_date: date
    visit_end_datetime: Optional[datetime] = None
    visit_type_concept_id: int
    provider_id: Optional[int] = None
    care_site_id: Optional[int] = None
    visit_source_value: Optional[str] = Field(None, max_length=50)
    visit_source_concept_id: Optional[int] = None
    admitting_source_concept_id: Optional[int] = None
    admitting_source_value: Optional[str] = Field(None, max_length=50)
    discharge_to_concept_id: Optional[int] = None
    discharge_to_source_value: Optional[str] = Field(None, max_length=50)
    preceding_visit_occurrence_id: Optional[int] = None
