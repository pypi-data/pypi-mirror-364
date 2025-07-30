from pydantic import Field
from ..base import OmopVocabularyModel


class Domain(OmopVocabularyModel):
    """
    OMOP Domain table representing standardized domains that group related concepts.

    Domains provide a high-level categorization of concepts and are used to
    organize the standardized vocabularies in the OMOP Common Data Model.
    """

    domain_id: str = Field(max_length=20)
    domain_name: str = Field(max_length=255)
    domain_concept_id: int
