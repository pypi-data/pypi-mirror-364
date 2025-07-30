from datetime import date
from typing import Optional

from pydantic import Field
from ..base import OmopReferenceModel


class CdmSource(OmopReferenceModel):
    """
    The CDM_SOURCE table contains detail about the source database and the process used to transform
    the data into the OMOP Common Data Model.
    """

    cdm_source_name: str = Field(max_length=255)
    cdm_source_abbreviation: Optional[str] = Field(None, max_length=25)
    cdm_holder: Optional[str] = Field(None, max_length=255)
    source_description: Optional[str] = None
    source_documentation_reference: Optional[str] = Field(None, max_length=255)
    cdm_etl_reference: Optional[str] = Field(None, max_length=255)
    source_release_date: Optional[date] = None
    cdm_release_date: Optional[date] = None
    cdm_version: Optional[str] = Field(None, max_length=10)
    vocabulary_version: Optional[str] = Field(None, max_length=20)
