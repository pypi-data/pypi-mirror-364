from typing import Optional
from pydantic import Field
from ..base import OmopReferenceModel


class Provider(OmopReferenceModel):
    """OMOP CDM Provider table model.

    Contains information about healthcare providers including their identifiers,
    demographics, and specialty information.
    """

    provider_id: int
    provider_name: Optional[str] = Field(None, max_length=255)
    npi: Optional[str] = Field(None, max_length=20)
    dea: Optional[str] = Field(None, max_length=20)
    specialty_concept_id: Optional[int] = None
    care_site_id: Optional[int] = None
    year_of_birth: Optional[int] = None
    gender_concept_id: Optional[int] = None
    provider_source_value: Optional[str] = Field(None, max_length=50)
    specialty_source_value: Optional[str] = Field(None, max_length=50)
    specialty_source_concept_id: Optional[int] = None
    gender_source_value: Optional[str] = Field(None, max_length=50)
    gender_source_concept_id: Optional[int] = None
