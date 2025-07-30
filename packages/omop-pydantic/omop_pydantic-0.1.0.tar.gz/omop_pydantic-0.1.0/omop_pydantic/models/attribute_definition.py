from typing import Optional
from pydantic import Field
from ..base import OmopReferenceModel


class AttributeDefinition(OmopReferenceModel):
    """
    Model representing the ATTRIBUTE_DEFINITION table from OMOP CDM.

    Stores definitions of attributes that can be associated with cohort definitions,
    drug exposure records and other entities in the OMOP CDM.
    """

    attribute_definition_id: int
    attribute_name: str = Field(max_length=255)
    attribute_description: Optional[str] = None
    attribute_type_concept_id: int
    attribute_syntax: Optional[str] = None
