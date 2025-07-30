from datetime import datetime, date
from typing import Optional
from pydantic import Field

from ..base import OmopClinicalModel


class Episode(OmopClinicalModel):
    """
    OMOP CDM EPISODE table.

    The EPISODE table aggregates lower-level clinical events (such as visits,
    drug exposures, diagnoses, and procedures) into a higher-level abstraction
    representing clinically meaningful episodes of care and disease phases,
    particularly for chronic conditions and cancer care.
    """

    episode_id: int
    person_id: int
    episode_concept_id: int
    episode_start_date: date
    episode_start_datetime: Optional[datetime] = None
    episode_end_date: Optional[date] = None
    episode_end_datetime: Optional[datetime] = None
    episode_parent_id: Optional[int] = None
    episode_number: Optional[int] = None
    episode_object_concept_id: int
    episode_type_concept_id: int
    episode_source_value: Optional[str] = Field(None, max_length=50)
    episode_source_concept_id: Optional[int] = None