"""
Tests for the Relationship model - focusing on semantic validation.
"""
import pytest
from datetime import date
from omop_pydantic.models.relationship import Relationship


class TestRelationshipSemantics:
    """Test Relationship model semantic validation."""

    def test_relationship_literal_validation(self):
        """Test that relationship_id accepts valid literal values."""
        # Common OMOP relationship IDs - these should be valid strings
        valid_relationships = [
            "Maps to",
            "Is a", 
            "Subsumes",
            "Mapped from",
            "Concept same_as to",
            "Concept alt_to to",
        ]
        
        for rel_id in valid_relationships:
            relationship = Relationship(
                relationship_id=rel_id,
                relationship_name=f"Test {rel_id}",
                is_hierarchical="1",
                defines_ancestry="1",
                reverse_relationship_id="Maps from" if rel_id == "Maps to" else "Is a",
                relationship_concept_id=44818790
            )
            assert relationship.relationship_id == rel_id

    def test_hierarchical_flag_validation(self):
        """Test is_hierarchical flag validation."""
        # Should accept "0" and "1"
        for flag_value in ["0", "1"]:
            relationship = Relationship(
                relationship_id="Is a",
                relationship_name="Is a",
                is_hierarchical=flag_value,
                defines_ancestry="1",
                reverse_relationship_id="Subsumes",
                relationship_concept_id=44818790
            )
            assert relationship.is_hierarchical == flag_value

    def test_ancestry_flag_validation(self):
        """Test defines_ancestry flag validation.""" 
        # Should accept "0" and "1"
        for flag_value in ["0", "1"]:
            relationship = Relationship(
                relationship_id="Is a",
                relationship_name="Is a",
                is_hierarchical="1",
                defines_ancestry=flag_value,
                reverse_relationship_id="Subsumes",
                relationship_concept_id=44818790
            )
            assert relationship.defines_ancestry == flag_value

    def test_bidirectional_relationship_consistency(self):
        """Test that bidirectional relationships are properly defined."""
        # Create a Maps to / Mapped from pair
        maps_to = Relationship(
            relationship_id="Maps to",
            relationship_name="Maps to",
            is_hierarchical="0",
            defines_ancestry="0", 
            reverse_relationship_id="Mapped from",
            relationship_concept_id=44818717
        )
        
        mapped_from = Relationship(
            relationship_id="Mapped from",
            relationship_name="Mapped from", 
            is_hierarchical="0",
            defines_ancestry="0",
            reverse_relationship_id="Maps to",
            relationship_concept_id=44818718
        )
        
        # Verify the bidirectional relationship
        assert maps_to.reverse_relationship_id == mapped_from.relationship_id
        assert mapped_from.reverse_relationship_id == maps_to.relationship_id
