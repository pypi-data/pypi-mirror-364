from datetime import date, datetime
from typing import Optional

from pydantic import Field
from ..base import OmopClinicalModel


class Note(OmopClinicalModel):
    """
    OMOP NOTE table - Contains clinical notes and text documents.

    The NOTE table captures unstructured information that was recorded by a
    provider about a patient in free text notes on a given date.
    """

    note_id: int
    person_id: int
    note_date: date
    note_datetime: Optional[datetime] = None
    note_type_concept_id: int
    note_class_concept_id: int
    note_title: Optional[str] = Field(None, max_length=250)
    note_text: str
    encoding_concept_id: int
    language_concept_id: int
    provider_id: Optional[int] = None
    visit_occurrence_id: Optional[int] = None
    visit_detail_id: Optional[int] = None
    note_source_value: Optional[str] = Field(None, max_length=50)
