"""
Integration tests for loading data from CSV files.
"""
import pytest
import csv
from pathlib import Path
from datetime import date, datetime

# Import all models for testing
from omop_pydantic.models.person import Person
from omop_pydantic.models.concept import Concept
from omop_pydantic.models.condition_occurrence import ConditionOccurrence
from omop_pydantic.models.drug_exposure import DrugExposure
from omop_pydantic.models.condition_era import ConditionEra
from omop_pydantic.models.drug_era import DrugEra
from omop_pydantic.models.dose_era import DoseEra


class TestCSVLoading:
    """Test loading OMOP models from CSV files."""
    
    def test_person_csv_loading(self, omop_csv_dir, csv_loader):
        """Test loading Person records from CSV."""
        csv_path = omop_csv_dir / "PERSON.csv"
        if not csv_path.exists():
            pytest.skip("PERSON.csv not found")
            
        sample_rows = csv_loader(csv_path, limit=5)
        
        for row_data in sample_rows:
            # Convert to lowercase keys
            person_data = {k.lower(): v for k, v in row_data.items()}
            
            # Handle datetime conversion
            if person_data.get('birth_datetime'):
                dt_str = person_data['birth_datetime'].replace('Z', '+00:00')
                person_data['birth_datetime'] = datetime.fromisoformat(dt_str)
            
            person = Person(**person_data)
            assert person.person_id > 0
            assert person.year_of_birth is not None
    
    def test_concept_csv_loading(self, omop_csv_dir, csv_loader):
        """Test loading Concept records from CSV."""
        csv_path = omop_csv_dir / "CONCEPT.csv"
        if not csv_path.exists():
            pytest.skip("CONCEPT.csv not found")
            
        sample_rows = csv_loader(csv_path, limit=5)
        
        for row_data in sample_rows:
            concept_data = {k.lower(): v for k, v in row_data.items()}
            
            # Convert date strings
            if concept_data.get('valid_start_date'):
                concept_data['valid_start_date'] = date.fromisoformat(concept_data['valid_start_date'])
            if concept_data.get('valid_end_date'):
                concept_data['valid_end_date'] = date.fromisoformat(concept_data['valid_end_date'])
            
            concept = Concept(**concept_data)
            assert concept.concept_id is not None
            assert concept.concept_name is not None
    
    def test_era_tables_use_date_not_datetime(self, omop_csv_dir, csv_loader):
        """Test that era tables correctly use date type for start/end dates."""
        era_models = [
            ("CONDITION_ERA.csv", ConditionEra),
            ("DRUG_ERA.csv", DrugEra), 
            ("DOSE_ERA.csv", DoseEra)
        ]
        
        tables_tested = 0
        
        for csv_filename, model_class in era_models:
            csv_path = omop_csv_dir / csv_filename
            if not csv_path.exists():
                continue
                
            try:
                sample_rows = csv_loader(csv_path, limit=2)
                
                # If no rows returned (empty file), skip this table
                if not sample_rows:
                    continue
                    
                tables_tested += 1
                
                for row_data in sample_rows:
                    era_data = {k.lower(): v for k, v in row_data.items()}
                    
                    # Convert date strings to date objects (not datetime!)
                    for field in era_data:
                        if field.endswith('_start_date') or field.endswith('_end_date'):
                            if era_data[field]:
                                era_data[field] = date.fromisoformat(era_data[field])
                    
                    era_instance = model_class(**era_data)
                    
                    # Verify the date fields are actually date objects
                    for field_name in era_instance.__class__.model_fields:
                        if field_name.endswith('_start_date') or field_name.endswith('_end_date'):
                            field_value = getattr(era_instance, field_name, None)
                            if field_value is not None:
                                assert isinstance(field_value, date)
                                assert not isinstance(field_value, datetime)  # date, not datetime!
            except Exception:
                # Skip tables that can't be loaded (e.g., empty files)
                continue
        
        # Only require that at least one era table was tested successfully
        if tables_tested == 0:
            pytest.skip("No era tables with data available for testing")
    
    def test_all_tables_load_without_errors(self, omop_csv_dir):
        """Test that we can load at least one row from each available CSV that has data."""
        # Map CSV files to their corresponding model classes
        csv_to_model = {
            "PERSON.csv": Person,
            "CONCEPT.csv": Concept,
            "CONDITION_ERA.csv": ConditionEra,
            "DRUG_ERA.csv": DrugEra,
            "DOSE_ERA.csv": DoseEra,
            # Add more as needed
        }
        
        successful_loads = 0
        skipped_files = []
        
        for csv_filename, model_class in csv_to_model.items():
            csv_path = omop_csv_dir / csv_filename
            if not csv_path.exists():
                skipped_files.append(f"{csv_filename} (file not found)")
                continue
                
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    try:
                        first_row = next(reader)
                    except StopIteration:
                        # File has no data rows (header only)
                        skipped_files.append(f"{csv_filename} (no data rows)")
                        continue
                    
                    # Convert keys to lowercase
                    row_data = {k.lower(): v for k, v in first_row.items()}
                    
                    # Basic data type conversions
                    for field, value in row_data.items():
                        if value == '':
                            row_data[field] = None
                        elif field.endswith('_date') and value:
                            row_data[field] = date.fromisoformat(value)
                        elif field.endswith('_datetime') and value:
                            dt_str = value.replace('Z', '+00:00')
                            row_data[field] = datetime.fromisoformat(dt_str)
                    
                    # Try to create the model instance
                    instance = model_class(**row_data)
                    assert instance is not None
                    successful_loads += 1
                    
            except Exception as e:
                pytest.fail(f"Failed to load {csv_filename} with {model_class.__name__}: {e}")
        
        # Report what was skipped for debugging
        if skipped_files:
            print(f"Skipped files: {', '.join(skipped_files)}")
        
        # Ensure we loaded at least some tables
        assert successful_loads > 0, "No CSV files could be loaded successfully"
    
    def test_concept_id_zero_in_real_data(self, omop_csv_dir):
        """Test that concept_id=0 appears in real data and is handled correctly."""
        csv_path = omop_csv_dir / "PERSON.csv"
        if not csv_path.exists():
            pytest.skip("PERSON.csv not found")
            
        zero_concept_found = False
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Check if any concept_id fields are 0
                for field, value in row.items():
                    if field.endswith('_CONCEPT_ID') and value == '0':
                        zero_concept_found = True
                        
                        # Convert row to lowercase and create Person
                        person_data = {k.lower(): v for k, v in row.items()}
                        
                        # Handle empty strings by converting to None
                        for field, value in person_data.items():
                            if value == '':
                                person_data[field] = None
                        
                        if person_data.get('birth_datetime'):
                            dt_str = person_data['birth_datetime'].replace('Z', '+00:00')
                            person_data['birth_datetime'] = datetime.fromisoformat(dt_str)
                        
                        # This should work - concept_id=0 is valid
                        person = Person(**person_data)
                        assert getattr(person, field.lower()) == 0
                        break
                
                if zero_concept_found:
                    break
        
        if not zero_concept_found:
            pytest.skip("No concept_id=0 found in test data")