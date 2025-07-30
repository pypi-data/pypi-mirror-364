from datetime import date
from typing import Optional

from ..base import OmopClinicalModel


class ConditionEra(OmopClinicalModel):
    """
    Condition eras represent spans of time when a person is assumed to have a given condition.
    A condition era is not the same as a condition occurrence record, but rather a time span
    where we believe a person had a particular condition.
    """

    condition_era_id: int
    person_id: int
    condition_concept_id: int
    condition_era_start_date: date
    condition_era_end_date: date
    condition_occurrence_count: Optional[int] = None
