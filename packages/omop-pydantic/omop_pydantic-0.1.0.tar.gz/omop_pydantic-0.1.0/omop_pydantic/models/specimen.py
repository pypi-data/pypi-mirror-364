from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import Field
from ..base import OmopClinicalModel


class Specimen(OmopClinicalModel):
    """
    The SPECIMEN table contains the records identifying biological samples from a person.
    """

    specimen_id: int
    person_id: int
    specimen_concept_id: int
    specimen_type_concept_id: int
    specimen_date: date
    specimen_datetime: Optional[datetime] = None
    quantity: Optional[Decimal] = None
    unit_concept_id: Optional[int] = None
    anatomic_site_concept_id: Optional[int] = None
    disease_status_concept_id: Optional[int] = None
    specimen_source_id: Optional[str] = Field(None, max_length=50)
    specimen_source_value: Optional[str] = Field(None, max_length=50)
    unit_source_value: Optional[str] = Field(None, max_length=50)
    anatomic_site_source_value: Optional[str] = Field(None, max_length=50)
    disease_status_source_value: Optional[str] = Field(None, max_length=50)
