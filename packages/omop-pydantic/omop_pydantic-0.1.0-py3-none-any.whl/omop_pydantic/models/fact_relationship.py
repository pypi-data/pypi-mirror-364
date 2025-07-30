from ..base import OmopReferenceModel


class FactRelationship(OmopReferenceModel):
    """
    OMOP CDM FACT_RELATIONSHIP table.

    This table contains records about the relationships between facts stored as
    records in any table of the CDM. Relationships can be defined between facts
    from the same domain, or different domains.
    """

    domain_concept_id_1: int
    fact_id_1: int
    domain_concept_id_2: int
    fact_id_2: int
    relationship_concept_id: int
