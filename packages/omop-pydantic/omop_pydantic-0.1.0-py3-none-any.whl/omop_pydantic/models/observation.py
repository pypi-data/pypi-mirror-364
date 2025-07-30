from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import Field
from ..base import OmopClinicalModel


class Observation(OmopClinicalModel):
    """
    OMOP CDM Observation table.

    The OBSERVATION table captures clinical facts about a Person obtained in the
    context of examination, questioning or a procedure. Any data that cannot be
    represented by any other domains, such as social and lifestyle facts, medical
    history, family history, etc. are recorded here.
    """

    observation_id: int
    person_id: int
    observation_concept_id: int
    observation_date: date
    observation_datetime: Optional[datetime] = None
    observation_type_concept_id: int
    value_as_number: Optional[Decimal] = None
    value_as_string: Optional[str] = Field(None, max_length=60)
    value_as_concept_id: Optional[int] = None
    qualifier_concept_id: Optional[int] = None
    unit_concept_id: Optional[int] = None
    provider_id: Optional[int] = None
    visit_occurrence_id: Optional[int] = None
    visit_detail_id: Optional[int] = None
    observation_source_value: Optional[str] = Field(None, max_length=50)
    observation_source_concept_id: Optional[int] = None
    unit_source_value: Optional[str] = Field(None, max_length=50)
    qualifier_source_value: Optional[str] = Field(None, max_length=50)
    # OMOP CDM 5.4 fields
    observation_event_id: Optional[int] = None
    obs_event_field_concept_id: Optional[int] = None
