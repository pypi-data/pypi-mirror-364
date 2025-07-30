from typing import Optional
from pydantic import Field
from ..base import OmopVocabularyModel


class Vocabulary(OmopVocabularyModel):
    """
    Vocabulary table from OMOP Common Data Model.
    Contains information about the vocabularies used in the CDM.
    """

    vocabulary_id: str = Field(max_length=20)
    vocabulary_name: str = Field(max_length=255)
    vocabulary_reference: str = Field(max_length=255)
    vocabulary_version: Optional[str] = Field(default=None, max_length=255)
    vocabulary_concept_id: int
