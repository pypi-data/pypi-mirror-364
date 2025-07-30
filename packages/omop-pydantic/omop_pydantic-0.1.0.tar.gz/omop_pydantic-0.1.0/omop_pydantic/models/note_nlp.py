from datetime import date, datetime
from typing import Optional

from pydantic import Field
from ..base import OmopReferenceModel


class NoteNlp(OmopReferenceModel):
    """
    The NOTE_NLP table encodes all output of NLP on clinical notes. Each row represents
    a single extracted term from a note.
    """

    note_nlp_id: int
    note_id: int
    section_concept_id: Optional[int] = None
    snippet: Optional[str] = Field(None, max_length=250)
    offset: Optional[str] = Field(None, max_length=50)
    lexical_variant: str = Field(max_length=250)
    note_nlp_concept_id: Optional[int] = None
    note_nlp_source_concept_id: Optional[int] = None
    nlp_system: Optional[str] = Field(None, max_length=250)
    nlp_date: date
    nlp_datetime: Optional[datetime] = None
    term_exists: Optional[str] = Field(None, max_length=1)
    term_temporal: Optional[str] = Field(None, max_length=50)
    term_modifiers: Optional[str] = Field(None, max_length=2000)
