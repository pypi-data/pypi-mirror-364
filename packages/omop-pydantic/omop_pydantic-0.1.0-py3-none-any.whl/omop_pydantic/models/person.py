from datetime import datetime
from typing import Optional

from pydantic import Field

from ..base import OmopClinicalModel


class Person(OmopClinicalModel):
    """
    The PERSON table contains records that uniquely identify each patient in the source data
    who is time at-risk to have clinical observations recorded within the source systems.
    """

    person_id: int
    gender_concept_id: int
    year_of_birth: int
    month_of_birth: Optional[int] = None
    day_of_birth: Optional[int] = None
    birth_datetime: Optional[datetime] = None
    race_concept_id: int
    ethnicity_concept_id: int
    location_id: Optional[int] = None
    provider_id: Optional[int] = None
    care_site_id: Optional[int] = None
    person_source_value: Optional[str] = Field(None, max_length=50)
    gender_source_value: Optional[str] = Field(None, max_length=50)
    gender_source_concept_id: Optional[int] = None
    race_source_value: Optional[str] = Field(None, max_length=50)
    race_source_concept_id: Optional[int] = None
    ethnicity_source_value: Optional[str] = Field(None, max_length=50)
    ethnicity_source_concept_id: Optional[int] = None
