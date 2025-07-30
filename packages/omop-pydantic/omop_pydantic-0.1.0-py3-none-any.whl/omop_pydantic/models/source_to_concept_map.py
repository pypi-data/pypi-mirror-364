from datetime import date
from typing import Optional, Literal

from pydantic import Field
from ..base import OmopVocabularyModel


class SourceToConceptMap(OmopVocabularyModel):
    """
    OMOP CDM Source to Concept Map table.

    Contains mappings from source codes to standard OMOP concepts,
    including validity periods and target vocabulary information.
    """

    source_code: str = Field(max_length=50)
    source_concept_id: int
    source_vocabulary_id: str = Field(max_length=20)
    source_code_description: Optional[str] = Field(default=None, max_length=255)
    target_concept_id: int
    target_vocabulary_id: str = Field(max_length=20)
    valid_start_date: date
    valid_end_date: date
    invalid_reason: Optional[Literal["D", "U"]] = None
