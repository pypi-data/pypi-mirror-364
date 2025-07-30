from datetime import date, datetime
from typing import Optional

from pydantic import Field
from ..base import OmopReferenceModel


class Metadata(OmopReferenceModel):
    """
    OMOP CDM Metadata table for storing metadata about the CDM instance.
    """

    metadata_concept_id: int
    metadata_type_concept_id: int
    name: str = Field(max_length=250)
    value_as_string: Optional[str] = Field(None, max_length=250)
    value_as_concept_id: Optional[int] = None
    metadata_date: Optional[date] = None
    metadata_datetime: Optional[datetime] = None
