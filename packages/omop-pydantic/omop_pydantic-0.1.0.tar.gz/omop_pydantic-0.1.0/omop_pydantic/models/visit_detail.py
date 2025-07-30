from datetime import date, datetime
from typing import Optional

from pydantic import Field
from ..base import OmopClinicalModel


class VisitDetail(OmopClinicalModel):
    """
    OMOP CDM Visit Detail table.

    The VISIT_DETAIL table is an optional table used to represent details
    of each record in the parent VISIT_OCCURRENCE table. A good example
    of this would be the movement between units in a hospital during an
    inpatient stay or claim lines associated with a one insurance claim.
    """

    visit_detail_id: int
    person_id: int
    visit_detail_concept_id: int
    visit_detail_start_date: date
    visit_detail_start_datetime: Optional[datetime] = None
    visit_detail_end_date: date
    visit_detail_end_datetime: Optional[datetime] = None
    visit_detail_type_concept_id: int
    provider_id: Optional[int] = None
    care_site_id: Optional[int] = None
    visit_detail_source_value: Optional[str] = Field(None, max_length=50)
    visit_detail_source_concept_id: Optional[int] = None
    admitting_source_value: Optional[str] = Field(None, max_length=50)
    admitting_source_concept_id: Optional[int] = None
    discharge_to_source_value: Optional[str] = Field(None, max_length=50)
    discharge_to_concept_id: Optional[int] = None
    preceding_visit_detail_id: Optional[int] = None
    visit_detail_parent_id: Optional[int] = None
    visit_occurrence_id: int
