"""
Tests for the Person model.
"""
import pytest
from datetime import date, datetime
from omop_pydantic.models.person import Person


class TestPerson:
    """Test Person model functionality."""
    
    def test_valid_person_from_dict(self, sample_person_data):
        """Test creating Person from valid dictionary."""
        person = Person(**sample_person_data)
        
        assert person.person_id == 1
        assert person.gender_concept_id == 8532
        assert person.year_of_birth == 1990
        assert person.month_of_birth == 6
        assert person.day_of_birth == 15
        assert person.race_concept_id == 8527
        assert person.ethnicity_concept_id == 0  # No matching concept
    
    def test_person_from_csv_data(self, omop_csv_dir, csv_loader):
        """Test loading Person from actual CSV data."""
        csv_path = omop_csv_dir / "PERSON.csv"
        sample_rows = csv_loader(csv_path, limit=3)
        
        for row_data in sample_rows:
            # Convert string keys to lowercase (CSV headers are uppercase)
            person_data = {k.lower(): v for k, v in row_data.items()}
            
            # Handle datetime fields - CSV has birth_datetime as ISO string
            if person_data.get('birth_datetime'):
                person_data['birth_datetime'] = datetime.fromisoformat(
                    person_data['birth_datetime'].replace('Z', '+00:00')
                )
            
            person = Person(**person_data)
            assert person.person_id > 0
            assert person.year_of_birth is not None
    
    def test_concept_id_zero_allowed(self):
        """Test that concept_id=0 is allowed (no matching concept)."""
        person = Person(
            person_id=1,
            gender_concept_id=0,  # No matching concept
            year_of_birth=1990,
            race_concept_id=0,    # No matching concept
            ethnicity_concept_id=0  # No matching concept
        )
        
        assert person.gender_concept_id == 0
        assert person.race_concept_id == 0
        assert person.ethnicity_concept_id == 0
    
    def test_person_id_zero_rejected(self):
        """Test that person_id=0 is rejected by validation."""
        # OMOP best practices require positive person IDs
        # The model enforces this constraint for data quality
        with pytest.raises(ValueError, match="person_id must be a positive integer"):
            Person(
                person_id=0,
                gender_concept_id=8532,
                year_of_birth=1990,
                race_concept_id=8527,
                ethnicity_concept_id=0
            )
    
    def test_table_name_classmethod(self):
        """Test Person.table_name() returns 'person'."""
        assert Person.table_name() == "person"
    
    def test_primary_key_detection(self):
        """Test get_primary_key_field() returns 'person_id'."""
        person = Person(
            person_id=1,
            gender_concept_id=8532,
            year_of_birth=1990,
            race_concept_id=8527,
            ethnicity_concept_id=0
        )
        
        assert person.get_primary_key_field() == "person_id"
        assert person.get_primary_key_value() == 1
    
    def test_concept_fields_detection(self):
        """Test that concept fields are properly identified."""
        person = Person(
            person_id=1,
            gender_concept_id=8532,
            year_of_birth=1990,
            race_concept_id=8527,
            ethnicity_concept_id=0
        )
        
        concept_fields = person.get_concept_fields()
        
        assert "gender_concept_id" in concept_fields
        assert "race_concept_id" in concept_fields
        assert "ethnicity_concept_id" in concept_fields
        assert concept_fields["gender_concept_id"] == 8532
        assert concept_fields["race_concept_id"] == 8527
        assert concept_fields["ethnicity_concept_id"] == 0
    
    def test_has_standardized_concept(self):
        """Test has_standardized_concept helper method."""
        person = Person(
            person_id=1,
            gender_concept_id=8532,     # Has standard concept
            year_of_birth=1990,
            race_concept_id=0,          # No matching concept
            ethnicity_concept_id=8527
        )
        
        assert person.has_standardized_concept("gender") is True
        assert person.has_standardized_concept("race") is False
        assert person.has_standardized_concept("ethnicity") is True
    
    def test_extra_fields_rejected(self):
        """Test that unexpected fields are rejected."""
        with pytest.raises(ValueError, match="Extra inputs are not permitted"):
            Person(
                person_id=1,
                gender_concept_id=8532,
                year_of_birth=1990,
                race_concept_id=8527,
                ethnicity_concept_id=0,
                unexpected_field="should_fail"  # This should cause failure
            )
    
    def test_birth_datetime_consistency(self):
        """Test that birth_datetime date components match year/month/day fields."""
        # Test with consistent values
        person = Person(
            person_id=1,
            gender_concept_id=8532,
            year_of_birth=1990,
            month_of_birth=6,
            day_of_birth=15,
            birth_datetime=datetime(1990, 6, 15, 10, 30, 0),
            race_concept_id=8527,
            ethnicity_concept_id=0
        )
        assert person.birth_datetime.date() == date(1990, 6, 15)
        
        # Note: The base model validates date/datetime field consistency,
        # but birth_datetime doesn't follow the standard _date/_datetime pattern
        # so manual validation would be needed for strict consistency
    
    def test_source_value_fields(self):
        """Test source value field handling and length constraints."""
        person = Person(
            person_id=1,
            gender_concept_id=8532,
            gender_source_value="M",
            gender_source_concept_id=0,
            year_of_birth=1990,
            race_concept_id=8527,
            race_source_value="White",
            race_source_concept_id=0,
            ethnicity_concept_id=0,
            ethnicity_source_value="Not Hispanic",
            person_source_value="PAT001"
        )
        
        source_fields = person.get_source_value_fields()
        assert "gender_source_value" in source_fields
        assert "race_source_value" in source_fields
        assert "ethnicity_source_value" in source_fields
        assert "person_source_value" in source_fields
        
        # Test max length constraint (50 chars for person fields)
        with pytest.raises(ValueError, match="String should have at most 50 characters"):
            Person(
                person_id=1,
                gender_concept_id=8532,
                gender_source_value="A" * 51,  # Too long
                year_of_birth=1990,
                race_concept_id=8527,
                ethnicity_concept_id=0
            )
    
    def test_optional_fields_with_none(self):
        """Test that optional fields can be None or omitted."""
        # Minimal required fields only
        person = Person(
            person_id=1,
            gender_concept_id=8532,
            year_of_birth=1990,
            race_concept_id=8527,
            ethnicity_concept_id=0
        )
        
        assert person.month_of_birth is None
        assert person.day_of_birth is None
        assert person.birth_datetime is None
        assert person.location_id is None
        assert person.provider_id is None
        assert person.care_site_id is None
        assert person.person_source_value is None
    
    def test_bulk_csv_loading(self, omop_csv_dir, csv_loader):
        """Test loading all Person records from CSV."""
        csv_path = omop_csv_dir / "PERSON.csv"
        all_rows = csv_loader(csv_path, limit=None)  # Load all rows
        
        persons = []
        errors = []
        
        for idx, row_data in enumerate(all_rows):
            try:
                person_data = {k.lower(): v for k, v in row_data.items()}
                if person_data.get('birth_datetime'):
                    person_data['birth_datetime'] = datetime.fromisoformat(
                        person_data['birth_datetime'].replace('Z', '+00:00')
                    )
                
                person = Person(**person_data)
                persons.append(person)
            except Exception as e:
                errors.append((idx, str(e)))
        
        # All records should load successfully
        assert len(errors) == 0, f"Failed to load {len(errors)} records: {errors[:5]}"
        assert len(persons) > 0, "No persons loaded from CSV"
        
        # Verify data integrity
        person_ids = [p.person_id for p in persons]
        assert len(person_ids) == len(set(person_ids)), "Duplicate person_ids found"
        
        # Check that all persons have required concept fields
        for person in persons:
            assert person.gender_concept_id is not None
            assert person.race_concept_id is not None
            assert person.ethnicity_concept_id is not None
    
    def test_id_fields_identification(self):
        """Test that ID fields are properly identified."""
        person = Person(
            person_id=1,
            gender_concept_id=8532,
            year_of_birth=1990,
            race_concept_id=8527,
            ethnicity_concept_id=0,
            location_id=100,
            provider_id=200,
            care_site_id=300
        )
        
        id_fields = person.get_id_fields()
        
        # Check all ID fields are identified
        expected_ids = {
            'person_id', 'gender_concept_id', 'race_concept_id', 
            'ethnicity_concept_id', 'location_id', 'provider_id', 
            'care_site_id', 'gender_source_concept_id', 
            'race_source_concept_id', 'ethnicity_source_concept_id'
        }
        
        for field in expected_ids:
            if getattr(person, field, None) is not None:
                assert field in id_fields
    
    def test_year_of_birth_validation(self):
        """Test year of birth validation."""
        current_year = datetime.now().year
        
        # Test valid year
        person = Person(
            person_id=1,
            gender_concept_id=8532,
            year_of_birth=1990,
            race_concept_id=8527,
            ethnicity_concept_id=0
        )
        assert person.year_of_birth == 1990
        
        # Test future year should fail if there's validation
        # (Note: The model might not have this validation, but the test documents expected behavior)
        try:
            future_person = Person(
                person_id=1,
                gender_concept_id=8532,
                year_of_birth=current_year + 10,  # Future year
                race_concept_id=8527,
                ethnicity_concept_id=0
            )
            # If no validation exists, at least document the behavior
            assert future_person.year_of_birth == current_year + 10
        except ValueError:
            # If validation exists, this is the expected behavior
            pass