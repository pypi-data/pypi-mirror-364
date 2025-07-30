from datetime import date
from typing import Optional

from pydantic import Field
from ..base import OmopReferenceModel


class CohortDefinition(OmopReferenceModel):
    """
    The COHORT_DEFINITION table contains records defining a patient cohort derived from the data through the associated description and syntax and upon instantiation (execution of the algorithm) placed into the COHORT table.
    """

    cohort_definition_id: int
    cohort_definition_name: str = Field(max_length=255)
    cohort_definition_description: Optional[str] = None
    definition_type_concept_id: int
    cohort_definition_syntax: Optional[str] = None
    subject_concept_id: int
    cohort_initiation_date: Optional[date] = None
