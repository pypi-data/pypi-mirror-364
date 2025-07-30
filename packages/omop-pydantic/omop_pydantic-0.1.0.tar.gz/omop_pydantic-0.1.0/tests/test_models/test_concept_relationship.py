"""Tests for the ConceptRelationship model."""
import pytest
from datetime import date
from omop_pydantic.models.concept_relationship import ConceptRelationship


class TestConceptRelationship:
    """Test ConceptRelationship model functionality."""

    def test_valid_concept_relationship_from_dict(self):
        """Test creating ConceptRelationship from valid dictionary."""
        data = {
            "concept_id_1": 8532,  # Gender concept
            "concept_id_2": 8507,  # Related concept
            "relationship_id": "Maps to",
            "valid_start_date": date(2020, 1, 1),
            "valid_end_date": date(2099, 12, 31),
            "invalid_reason": None
        }
        
        rel = ConceptRelationship(**data)
        assert rel.concept_id_1 == 8532
        assert rel.concept_id_2 == 8507
        assert rel.relationship_id == "Maps to"
        assert rel.valid_start_date == date(2020, 1, 1)
        assert rel.valid_end_date == date(2099, 12, 31)
        assert rel.invalid_reason is None

    def test_concept_relationship_from_csv(self, omop_csv_dir, csv_loader):
        """Test loading ConceptRelationship from CSV data."""
        csv_path = omop_csv_dir / "CONCEPT_RELATIONSHIP.csv"
        if not csv_path.exists():
            pytest.skip("CONCEPT_RELATIONSHIP.csv not found")
            
        sample_rows = csv_loader(csv_path, limit=5)
        
        for row_data in sample_rows:
            # Convert to lowercase
            rel_data = {k.lower(): v for k, v in row_data.items()}
            
            # Convert dates
            if rel_data.get('valid_start_date'):
                rel_data['valid_start_date'] = date.fromisoformat(rel_data['valid_start_date'])
            if rel_data.get('valid_end_date'):
                rel_data['valid_end_date'] = date.fromisoformat(rel_data['valid_end_date'])
            
            rel = ConceptRelationship(**rel_data)
            assert rel.concept_id_1 is not None
            assert rel.concept_id_2 is not None
            assert rel.relationship_id is not None

    def test_relationship_types(self, omop_csv_dir, csv_loader):
        """Test common relationship types in concept relationships."""
        csv_path = omop_csv_dir / "CONCEPT_RELATIONSHIP.csv"
        if not csv_path.exists():
            pytest.skip("CONCEPT_RELATIONSHIP.csv not found")
            
        sample_rows = csv_loader(csv_path, limit=100)
        
        relationship_types = set()
        for row in sample_rows:
            rel_id = row.get('RELATIONSHIP_ID', row.get('relationship_id'))
            if rel_id:
                relationship_types.add(rel_id)
        
        # Common OMOP relationship types
        common_types = {"Maps to", "Is a", "Subsumes", "Mapped from"}
        found_common = relationship_types.intersection(common_types)
        assert len(found_common) > 0, f"Expected some common relationship types, found: {relationship_types}"

    def test_bidirectional_relationships(self, omop_csv_dir, csv_loader):
        """Test that relationships often have bidirectional counterparts."""
        csv_path = omop_csv_dir / "CONCEPT_RELATIONSHIP.csv"
        if not csv_path.exists():
            pytest.skip("CONCEPT_RELATIONSHIP.csv not found")
            
        sample_rows = csv_loader(csv_path, limit=200)
        
        # Track relationships
        forward_rels = {}
        reverse_rels = {}
        
        for row in sample_rows:
            c1 = row.get('CONCEPT_ID_1', row.get('concept_id_1'))
            c2 = row.get('CONCEPT_ID_2', row.get('concept_id_2'))
            rel_type = row.get('RELATIONSHIP_ID', row.get('relationship_id'))
            
            if c1 and c2 and rel_type:
                key = (int(c1), int(c2))
                forward_rels[key] = rel_type
                
                # Check for reverse
                reverse_key = (int(c2), int(c1))
                if reverse_key in forward_rels:
                    reverse_rels[reverse_key] = forward_rels[reverse_key]
        
        # Should find at least some bidirectional relationships
        assert len(reverse_rels) > 0, "Expected to find bidirectional relationships"

    def test_validity_date_validation(self):
        """Test that valid_start_date must be before valid_end_date."""
        # Valid date range
        rel = ConceptRelationship(
            concept_id_1=1,
            concept_id_2=2,
            relationship_id="Maps to",
            valid_start_date=date(2020, 1, 1),
            valid_end_date=date(2099, 12, 31)
        )
        assert rel.valid_start_date < rel.valid_end_date
        
        # Invalid date range
        with pytest.raises(ValueError, match="valid_start_date.*must be before or equal to.*valid_end_date"):
            ConceptRelationship(
                concept_id_1=1,
                concept_id_2=2,
                relationship_id="Maps to",
                valid_start_date=date(2099, 12, 31),
                valid_end_date=date(2020, 1, 1)
            )

    def test_invalid_reason_literal(self):
        """Test invalid_reason Literal validation."""
        # Valid values
        for value in ['D', 'U', None]:
            rel = ConceptRelationship(
                concept_id_1=1,
                concept_id_2=2,
                relationship_id="Maps to",
                valid_start_date=date(2020, 1, 1),
                valid_end_date=date(2099, 12, 31),
                invalid_reason=value
            )
            assert rel.invalid_reason == value
        
        # Invalid value
        with pytest.raises(ValueError):
            ConceptRelationship(
                concept_id_1=1,
                concept_id_2=2,
                relationship_id="Maps to",
                valid_start_date=date(2020, 1, 1),
                valid_end_date=date(2099, 12, 31),
                invalid_reason="X"  # Invalid
            )

    def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValueError, match="Extra inputs are not permitted"):
            ConceptRelationship(
                concept_id_1=1,
                concept_id_2=2,
                relationship_id="Maps to",
                valid_start_date=date(2020, 1, 1),
                valid_end_date=date(2099, 12, 31),
                extra_field="not_allowed"
            )

    def test_table_name_classmethod(self):
        """Test table_name() returns correct snake_case name."""
        assert ConceptRelationship.table_name() == "concept_relationship"

    def test_field_identification(self):
        """Test field type identification."""
        rel = ConceptRelationship(
            concept_id_1=1,
            concept_id_2=2,
            relationship_id="Maps to",
            valid_start_date=date(2020, 1, 1),
            valid_end_date=date(2099, 12, 31)
        )
        
        # Check ID fields
        id_fields = rel.get_id_fields()
        assert 'concept_id_1' in id_fields
        assert 'concept_id_2' in id_fields
        # relationship_id is an ID but doesn't end with _id
        
        # Check date fields
        temporal_fields = rel.get_temporal_fields()
        assert 'valid_start_date' in temporal_fields
        assert 'valid_end_date' in temporal_fields

    def test_bulk_loading(self, omop_csv_dir, csv_loader):
        """Test bulk loading of concept relationships."""
        csv_path = omop_csv_dir / "CONCEPT_RELATIONSHIP.csv"
        if not csv_path.exists():
            pytest.skip("CONCEPT_RELATIONSHIP.csv not found")
            
        all_rows = csv_loader(csv_path, limit=500)  # Sample for performance
        
        relationships = []
        errors = []
        
        for idx, row_data in enumerate(all_rows):
            try:
                rel_data = {k.lower(): v for k, v in row_data.items()}
                if rel_data.get('valid_start_date'):
                    rel_data['valid_start_date'] = date.fromisoformat(rel_data['valid_start_date'])
                if rel_data.get('valid_end_date'):
                    rel_data['valid_end_date'] = date.fromisoformat(rel_data['valid_end_date'])
                
                rel = ConceptRelationship(**rel_data)
                relationships.append(rel)
            except Exception as e:
                errors.append((idx, str(e)))
        
        # All records should load successfully
        assert len(errors) == 0, f"Failed to load {len(errors)} records: {errors[:5]}"
        assert len(relationships) > 0, "No relationships loaded from CSV"
        
        # Verify some have invalid_reason set
        invalid_count = sum(1 for r in relationships if r.invalid_reason is not None)
        print(f"Found {invalid_count} invalid relationships out of {len(relationships)}")

    def test_primary_key_detection(self):
        """Test get_primary_key_field() for composite key model."""
        rel = ConceptRelationship(
            concept_id_1=1,
            concept_id_2=2,
            relationship_id="Maps to",
            valid_start_date=date(2020, 1, 1),
            valid_end_date=date(2099, 12, 31)
        )
        
        # ConceptRelationship has composite key, so no single primary key
        pk = rel.get_primary_key_field()
        assert pk is None  # No single PK field matches table_name + '_id'