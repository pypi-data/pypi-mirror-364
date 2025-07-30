from datetime import date
from typing import Optional, Literal

from pydantic import Field
from ..base import OmopVocabularyModel


class ConceptRelationship(OmopVocabularyModel):
    """
    OMOP CDM CONCEPT_RELATIONSHIP table.

    This table contains relationships between concepts, including hierarchical
    relationships, mappings, and semantic relationships.
    """

    concept_id_1: int
    concept_id_2: int
    relationship_id: str = Field(max_length=20)
    valid_start_date: date
    valid_end_date: date
    invalid_reason: Optional[Literal["D", "U"]] = None
