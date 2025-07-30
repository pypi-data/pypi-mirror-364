from pydantic import Field
from ..base import OmopVocabularyModel


class ConceptClass(OmopVocabularyModel):
    """
    OMOP CDM Concept Class table.

    Defines the concept classes used in the OMOP CDM to categorize concepts
    by their semantic meaning and use case within the vocabulary.
    """

    concept_class_id: str = Field(max_length=20)
    concept_class_name: str = Field(max_length=255)
    concept_class_concept_id: int
