from datetime import date
from typing import Optional, Literal

from pydantic import Field
from ..base import OmopVocabularyModel


class Concept(OmopVocabularyModel):
    """OMOP Concept table model.

    The Concept table contains records that uniquely identify each fundamental unit of
    meaning used to express clinical information in all domain tables of the CDM.
    """

    concept_id: int
    concept_name: str = Field(max_length=255)
    domain_id: str = Field(max_length=20)
    vocabulary_id: str = Field(max_length=20)
    concept_class_id: str = Field(max_length=20)
    standard_concept: Optional[Literal["S", "C"]] = None
    concept_code: str = Field(max_length=50)
    valid_start_date: date
    valid_end_date: date
    invalid_reason: Optional[Literal["D", "U"]] = None
