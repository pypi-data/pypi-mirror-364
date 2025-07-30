from datetime import date, datetime
from typing import Optional

from pydantic import Field

from ..base import OmopClinicalModel


class ProcedureOccurrence(OmopClinicalModel):
    """
    OMOP CDM PROCEDURE_OCCURRENCE table model.

    Records procedures performed on a person, including surgical procedures,
    diagnostic procedures, and other medical interventions.
    """

    procedure_occurrence_id: int
    person_id: int
    procedure_concept_id: int
    procedure_date: date
    procedure_datetime: Optional[datetime] = None
    procedure_type_concept_id: int
    modifier_concept_id: Optional[int] = None
    quantity: Optional[int] = None
    provider_id: Optional[int] = None
    visit_occurrence_id: Optional[int] = None
    visit_detail_id: Optional[int] = None
    procedure_source_value: Optional[str] = Field(None, max_length=50)
    procedure_source_concept_id: Optional[int] = None
    modifier_source_value: Optional[str] = Field(None, max_length=50)
