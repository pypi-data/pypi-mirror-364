from ..base import OmopReferenceModel


class EpisodeEvent(OmopReferenceModel):
    """
    OMOP CDM EPISODE_EVENT table.

    This table serves as a connector linking specific clinical events to episodes.
    It allows any record in standardized clinical events tables (e.g., condition_occurrence,
    drug_exposure, procedure_occurrence, measurement) to be associated with a higher-level
    episode abstraction for disease phases and treatment periods.
    """

    episode_id: int
    event_id: int
    episode_event_field_concept_id: int