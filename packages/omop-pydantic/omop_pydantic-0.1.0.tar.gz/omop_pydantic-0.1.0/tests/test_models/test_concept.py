"""
Tests for the Concept model and Literal guards.
"""
import pytest
from datetime import date
from omop_pydantic.models.concept import Concept


class TestConcept:
    """Test Concept model functionality."""
    
    def test_valid_concept_from_dict(self, sample_concept_data):
        """Test creating Concept from valid dictionary."""
        concept_data = sample_concept_data.copy()
        concept_data['valid_start_date'] = date.fromisoformat(concept_data['valid_start_date'])
        concept_data['valid_end_date'] = date.fromisoformat(concept_data['valid_end_date'])
        
        concept = Concept(**concept_data)
        
        assert concept.concept_id == 8532
        assert concept.concept_name == "FEMALE"
        assert concept.standard_concept == "S"
        assert concept.invalid_reason is None
    
    def test_concept_from_csv_data(self, omop_csv_dir, csv_loader):
        """Test loading Concept from actual CSV data."""
        csv_path = omop_csv_dir / "CONCEPT.csv"
        if not csv_path.exists():
            pytest.skip("CONCEPT.csv not found in test data")
            
        sample_rows = csv_loader(csv_path, limit=3)
        
        for row_data in sample_rows:
            # Convert string keys to lowercase
            concept_data = {k.lower(): v for k, v in row_data.items()}
            
            # Convert date strings to date objects
            if concept_data.get('valid_start_date'):
                concept_data['valid_start_date'] = date.fromisoformat(concept_data['valid_start_date'])
            if concept_data.get('valid_end_date'):
                concept_data['valid_end_date'] = date.fromisoformat(concept_data['valid_end_date'])
            
            concept = Concept(**concept_data)
            assert concept.concept_id is not None
            assert concept.concept_name is not None


class TestStandardConceptLiterals:
    """Test standard_concept Literal guards."""
    
    def test_standard_concept_accepts_s(self):
        """Test standard_concept accepts 'S' (Standard)."""
        concept = Concept(
            concept_id=1,
            concept_name="Test",
            domain_id="Test",
            vocabulary_id="Test", 
            concept_class_id="Test",
            standard_concept="S",  # Should be valid
            concept_code="TEST",
            valid_start_date=date(2020, 1, 1),
            valid_end_date=date(2099, 12, 31)
        )
        assert concept.standard_concept == "S"
    
    def test_standard_concept_accepts_c(self):
        """Test standard_concept accepts 'C' (Classification).""" 
        concept = Concept(
            concept_id=1,
            concept_name="Test",
            domain_id="Test",
            vocabulary_id="Test",
            concept_class_id="Test", 
            standard_concept="C",  # Should be valid
            concept_code="TEST",
            valid_start_date=date(2020, 1, 1),
            valid_end_date=date(2099, 12, 31)
        )
        assert concept.standard_concept == "C"
    
    def test_standard_concept_accepts_none(self):
        """Test standard_concept accepts None."""
        concept = Concept(
            concept_id=1,
            concept_name="Test", 
            domain_id="Test",
            vocabulary_id="Test",
            concept_class_id="Test",
            standard_concept=None,  # Should be valid
            concept_code="TEST",
            valid_start_date=date(2020, 1, 1),
            valid_end_date=date(2099, 12, 31)
        )
        assert concept.standard_concept is None
    
    def test_standard_concept_rejects_invalid(self):
        """Test standard_concept rejects invalid values."""
        with pytest.raises(ValueError):
            Concept(
                concept_id=1,
                concept_name="Test",
                domain_id="Test",
                vocabulary_id="Test",
                concept_class_id="Test",
                standard_concept="X",  # Should fail
                concept_code="TEST",
                valid_start_date=date(2020, 1, 1),
                valid_end_date=date(2099, 12, 31)
            )


class TestInvalidReasonLiterals:
    """Test invalid_reason Literal guards."""
    
    def test_invalid_reason_accepts_d(self):
        """Test invalid_reason accepts 'D' (Deprecated)."""
        concept = Concept(
            concept_id=1,
            concept_name="Test",
            domain_id="Test",
            vocabulary_id="Test",
            concept_class_id="Test",
            concept_code="TEST",
            valid_start_date=date(2020, 1, 1),
            valid_end_date=date(2099, 12, 31),
            invalid_reason="D"  # Should be valid
        )
        assert concept.invalid_reason == "D"
    
    def test_invalid_reason_accepts_u(self):
        """Test invalid_reason accepts 'U' (Updated)."""
        concept = Concept(
            concept_id=1,
            concept_name="Test",
            domain_id="Test", 
            vocabulary_id="Test",
            concept_class_id="Test",
            concept_code="TEST",
            valid_start_date=date(2020, 1, 1),
            valid_end_date=date(2099, 12, 31),
            invalid_reason="U"  # Should be valid
        )
        assert concept.invalid_reason == "U"
    
    def test_invalid_reason_accepts_none(self):
        """Test invalid_reason accepts None."""
        concept = Concept(
            concept_id=1,
            concept_name="Test",
            domain_id="Test",
            vocabulary_id="Test", 
            concept_class_id="Test",
            concept_code="TEST",
            valid_start_date=date(2020, 1, 1),
            valid_end_date=date(2099, 12, 31),
            invalid_reason=None  # Should be valid
        )
        assert concept.invalid_reason is None
    
    def test_invalid_reason_rejects_invalid(self):
        """Test invalid_reason rejects invalid values."""
        with pytest.raises(ValueError):
            Concept(
                concept_id=1,
                concept_name="Test",
                domain_id="Test",
                vocabulary_id="Test",
                concept_class_id="Test", 
                concept_code="TEST",
                valid_start_date=date(2020, 1, 1),
                valid_end_date=date(2099, 12, 31),
                invalid_reason="X"  # Should fail
            )


class TestConceptTableName:
    """Test Concept table name functionality."""
    
    def test_table_name_classmethod(self):
        """Test Concept.table_name() returns 'concept'."""
        assert Concept.table_name() == "concept"


class TestConceptRelationships:
    """Test Concept relationships and validation."""
    
    def test_validity_date_validation(self):
        """Test that valid_start_date must be before valid_end_date."""
        # Valid date range
        concept = Concept(
            concept_id=1,
            concept_name="Test",
            domain_id="Test",
            vocabulary_id="Test",
            concept_class_id="Test",
            concept_code="TEST",
            valid_start_date=date(2020, 1, 1),
            valid_end_date=date(2099, 12, 31)
        )
        assert concept.valid_start_date < concept.valid_end_date
        
        # Invalid date range (start after end)
        with pytest.raises(ValueError, match="valid_start_date.*must be before or equal to.*valid_end_date"):
            Concept(
                concept_id=1,
                concept_name="Test",
                domain_id="Test",
                vocabulary_id="Test",
                concept_class_id="Test",
                concept_code="TEST",
                valid_start_date=date(2099, 12, 31),
                valid_end_date=date(2020, 1, 1)
            )
    
    def test_concept_with_relationships(self, omop_csv_dir, csv_loader):
        """Test loading concepts and their relationships."""
        # Load concept
        concept_path = omop_csv_dir / "CONCEPT.csv"
        if not concept_path.exists():
            pytest.skip("CONCEPT.csv not found")
            
        concept_rows = csv_loader(concept_path, limit=5)
        concepts = []
        
        for row in concept_rows:
            data = {k.lower(): v for k, v in row.items()}
            if data.get('valid_start_date'):
                data['valid_start_date'] = date.fromisoformat(data['valid_start_date'])
            if data.get('valid_end_date'):
                data['valid_end_date'] = date.fromisoformat(data['valid_end_date'])
            concepts.append(Concept(**data))
        
        # Load concept relationships
        rel_path = omop_csv_dir / "CONCEPT_RELATIONSHIP.csv"
        if rel_path.exists():
            rel_rows = csv_loader(rel_path, limit=10)
            
            # Track concept IDs that have relationships
            concept_ids_with_rels = set()
            for row in rel_rows:
                data = {k.lower(): v for k, v in row.items()}
                if data.get('concept_id_1'):
                    concept_ids_with_rels.add(int(data['concept_id_1']))
                if data.get('concept_id_2'):
                    concept_ids_with_rels.add(int(data['concept_id_2']))
            
            # Verify we found some relationships
            assert len(concept_ids_with_rels) > 0
    
    def test_bulk_concept_loading(self, omop_csv_dir, csv_loader):
        """Test loading all Concept records from CSV."""
        csv_path = omop_csv_dir / "CONCEPT.csv"
        if not csv_path.exists():
            pytest.skip("CONCEPT.csv not found")
            
        all_rows = csv_loader(csv_path, limit=100)  # Load first 100 for speed
        
        concepts = []
        errors = []
        
        for idx, row_data in enumerate(all_rows):
            try:
                concept_data = {k.lower(): v for k, v in row_data.items()}
                if concept_data.get('valid_start_date'):
                    concept_data['valid_start_date'] = date.fromisoformat(concept_data['valid_start_date'])
                if concept_data.get('valid_end_date'):
                    concept_data['valid_end_date'] = date.fromisoformat(concept_data['valid_end_date'])
                
                concept = Concept(**concept_data)
                concepts.append(concept)
            except Exception as e:
                errors.append((idx, str(e)))
        
        # All records should load successfully
        assert len(errors) == 0, f"Failed to load {len(errors)} records: {errors[:5]}"
        assert len(concepts) > 0, "No concepts loaded from CSV"
        
        # Verify data integrity
        concept_ids = [c.concept_id for c in concepts]
        assert len(concept_ids) == len(set(concept_ids)), "Duplicate concept_ids found"
        
        # Check vocabulary diversity
        vocabularies = {c.vocabulary_id for c in concepts}
        assert len(vocabularies) > 1, "Expected multiple vocabularies"
        
        # Check domain diversity  
        domains = {c.domain_id for c in concepts}
        assert len(domains) > 1, "Expected multiple domains"
    
    def test_concept_code_uniqueness_within_vocabulary(self, omop_csv_dir, csv_loader):
        """Test that concept codes are unique within a vocabulary."""
        csv_path = omop_csv_dir / "CONCEPT.csv"
        if not csv_path.exists():
            pytest.skip("CONCEPT.csv not found")
            
        all_rows = csv_loader(csv_path, limit=1000)  # Sample size
        
        # Track concept_code per vocabulary
        vocab_codes = {}
        
        for row in all_rows:
            data = {k.lower(): v for k, v in row.items()}
            vocab_id = data.get('vocabulary_id')
            concept_code = data.get('concept_code')
            
            if vocab_id and concept_code:
                if vocab_id not in vocab_codes:
                    vocab_codes[vocab_id] = set()
                    
                # Check for duplicates
                assert concept_code not in vocab_codes[vocab_id], \
                    f"Duplicate concept_code '{concept_code}' in vocabulary '{vocab_id}'"
                    
                vocab_codes[vocab_id].add(concept_code)
    
    def test_concept_field_identification(self):
        """Test that concept model fields are properly categorized."""
        concept = Concept(
            concept_id=1,
            concept_name="Test",
            domain_id="Test",
            vocabulary_id="Test",
            concept_class_id="Test",
            concept_code="TEST",
            valid_start_date=date(2020, 1, 1),
            valid_end_date=date(2099, 12, 31)
        )
        
        # Check ID fields
        id_fields = concept.get_id_fields()
        assert 'concept_id' in id_fields
        assert 'concept_class_id' in id_fields
        
        # Check date fields
        temporal_fields = concept.get_temporal_fields()
        assert 'valid_start_date' in temporal_fields
        assert 'valid_end_date' in temporal_fields
        
        # Concept model shouldn't have concept fields (it IS a concept)
        concept_fields = concept.get_concept_fields()
        assert len(concept_fields) == 0
    
    def test_concept_string_field_lengths(self):
        """Test string field length constraints."""
        # Test with valid lengths
        concept = Concept(
            concept_id=1,
            concept_name="A" * 255,  # Max length
            domain_id="A" * 20,
            vocabulary_id="A" * 20,
            concept_class_id="A" * 20,
            concept_code="A" * 50,
            valid_start_date=date(2020, 1, 1),
            valid_end_date=date(2099, 12, 31)
        )
        assert len(concept.concept_name) == 255
        
        # Test exceeding max length
        with pytest.raises(ValueError, match="String should have at most 255 characters"):
            Concept(
                concept_id=1,
                concept_name="A" * 256,  # Too long
                domain_id="Test",
                vocabulary_id="Test",
                concept_class_id="Test",
                concept_code="TEST",
                valid_start_date=date(2020, 1, 1),
                valid_end_date=date(2099, 12, 31)
            )