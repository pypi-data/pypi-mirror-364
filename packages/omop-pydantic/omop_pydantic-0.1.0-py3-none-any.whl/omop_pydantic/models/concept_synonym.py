from pydantic import Field
from ..base import OmopVocabularyModel


class ConceptSynonym(OmopVocabularyModel):
    """
    OMOP CDM CONCEPT_SYNONYM table.

    Contains synonym names for concepts in different languages.
    """

    concept_id: int
    concept_synonym_name: str = Field(max_length=1000)
    language_concept_id: int
