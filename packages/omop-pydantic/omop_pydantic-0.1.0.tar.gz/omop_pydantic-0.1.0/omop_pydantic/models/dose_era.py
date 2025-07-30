from datetime import date
from decimal import Decimal
from ..base import OmopClinicalModel


class DoseEra(OmopClinicalModel):
    """
    OMOP CDM table representing dose eras for drug exposures.
    A dose era is a span of time when a person is assumed to be exposed to
    a constant dose of a specific drug.
    """

    dose_era_id: int
    person_id: int
    drug_concept_id: int
    unit_concept_id: int
    dose_value: Decimal
    dose_era_start_date: date
    dose_era_end_date: date
