from datetime import date
from decimal import Decimal
from typing import Optional, Literal

from pydantic import Field
from ..base import OmopVocabularyModel


class DrugStrength(OmopVocabularyModel):
    """
    OMOP CDM table for drug strength information.

    Contains the strength-related information for drug products, including
    amount values, units, and validity periods for the drug strength data.
    """

    drug_concept_id: int
    ingredient_concept_id: int
    amount_value: Optional[Decimal] = None
    amount_unit_concept_id: Optional[int] = None
    numerator_value: Optional[Decimal] = None
    numerator_unit_concept_id: Optional[int] = None
    denominator_value: Optional[Decimal] = None
    denominator_unit_concept_id: Optional[int] = None
    box_size: Optional[int] = None
    valid_start_date: date
    valid_end_date: date
    invalid_reason: Optional[Literal["D", "U"]] = None
