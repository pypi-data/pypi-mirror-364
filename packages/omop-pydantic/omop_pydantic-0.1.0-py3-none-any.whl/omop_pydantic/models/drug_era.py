from datetime import date
from typing import Optional

from ..base import OmopClinicalModel


class DrugEra(OmopClinicalModel):
    """
    A Drug Era is defined as a span of time when the Person is assumed to be exposed to a particular drug.
    Successive periods of Drug Exposures are combined under certain rules to produce continuous Drug Eras.
    """

    drug_era_id: int
    person_id: int
    drug_concept_id: int
    drug_era_start_date: date
    drug_era_end_date: date
    drug_exposure_count: Optional[int] = None
    gap_days: Optional[int] = None
