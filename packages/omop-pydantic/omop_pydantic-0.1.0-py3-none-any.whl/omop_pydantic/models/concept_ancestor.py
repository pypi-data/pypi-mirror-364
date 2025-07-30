from ..base import OmopVocabularyModel


class ConceptAncestor(OmopVocabularyModel):
    """
    The CONCEPT_ANCESTOR table contains relationships between concepts that are hierarchical,
    providing both direct and indirect ancestor-descendant relationships with separation levels.
    """

    ancestor_concept_id: int
    descendant_concept_id: int
    min_levels_of_separation: int
    max_levels_of_separation: int
