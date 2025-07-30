from datetime import date
from ..base import OmopClinicalModel


class ObservationPeriod(OmopClinicalModel):
    """
    Represents observation periods for persons in the OMOP Common Data Model.

    This table contains records that define spans of time during which a person
    is at-risk to have clinical events recorded within the source systems.
    """

    observation_period_id: int
    person_id: int
    observation_period_start_date: date
    observation_period_end_date: date
    period_type_concept_id: int
