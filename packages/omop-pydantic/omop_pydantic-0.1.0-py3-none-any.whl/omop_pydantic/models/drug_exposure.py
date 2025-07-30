from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import Field
from ..base import OmopClinicalModel


class DrugExposure(OmopClinicalModel):
    """
    OMOP CDM Drug Exposure table.

    This table captures records about the exposure to a Drug ingested or otherwise introduced
    into the body. A Drug is a biochemical substance formulated in such a way that when
    administered to a Person it will exert a certain physiological effect.
    """

    drug_exposure_id: int
    person_id: int
    drug_concept_id: int
    drug_exposure_start_date: date
    drug_exposure_start_datetime: Optional[datetime] = None
    drug_exposure_end_date: date
    drug_exposure_end_datetime: Optional[datetime] = None
    verbatim_end_date: Optional[date] = None
    drug_type_concept_id: int
    stop_reason: Optional[str] = Field(None, max_length=20)
    refills: Optional[int] = None
    quantity: Optional[Decimal] = None
    days_supply: Optional[int] = None
    sig: Optional[str] = None
    route_concept_id: Optional[int] = None
    lot_number: Optional[str] = Field(None, max_length=50)
    provider_id: Optional[int] = None
    visit_occurrence_id: Optional[int] = None
    visit_detail_id: Optional[int] = None
    drug_source_value: Optional[str] = Field(None, max_length=50)
    drug_source_concept_id: Optional[int] = None
    route_source_value: Optional[str] = Field(None, max_length=50)
    dose_unit_source_value: Optional[str] = Field(None, max_length=50)
