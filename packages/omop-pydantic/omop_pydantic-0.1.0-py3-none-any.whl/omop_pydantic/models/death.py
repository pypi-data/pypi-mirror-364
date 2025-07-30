from datetime import date, datetime
from typing import Optional

from pydantic import Field
from ..base import OmopClinicalModel


class Death(OmopClinicalModel):
    """
    OMOP CDM Death table for recording death information for a person.

    This table captures information about the death of a person, including
    the date and time of death, the type of death record, and cause of death.
    """

    person_id: int
    death_date: date
    death_datetime: Optional[datetime] = None
    death_type_concept_id: Optional[int] = None
    cause_concept_id: Optional[int] = None
    cause_source_value: Optional[str] = Field(default=None, max_length=50)
    cause_source_concept_id: Optional[int] = None
