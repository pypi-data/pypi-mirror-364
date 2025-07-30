from typing import Literal
from pydantic import Field
from ..base import OmopVocabularyModel


class Relationship(OmopVocabularyModel):
    """
    The RELATIONSHIP table contains records that define relations between Concepts.
    This table defines the semantic relationships between concepts in the OMOP vocabulary.
    """

    relationship_id: str = Field(max_length=20)
    relationship_name: str = Field(max_length=255)
    is_hierarchical: Literal["0", "1"]
    defines_ancestry: Literal["0", "1"]
    reverse_relationship_id: str = Field(max_length=20)
    relationship_concept_id: int
