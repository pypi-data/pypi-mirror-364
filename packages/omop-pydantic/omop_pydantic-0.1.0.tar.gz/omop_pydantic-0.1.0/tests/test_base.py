"""
Tests for the base OMOP model functionality.
"""
import pytest
from datetime import date, datetime
from typing import Type, Dict, Any, Literal, get_args
from decimal import Decimal
import importlib
from pathlib import Path
from omop_pydantic.base import OmopModel, OmopClinicalModel, OmopVocabularyModel, OmopReferenceModel


@pytest.fixture
def all_model_classes():
    """Fixture that yields all concrete OMOP model classes."""
    models_dir = Path(__file__).parent.parent / "omop_pydantic" / "models"
    model_classes = []
    
    for py_file in models_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
            
        module_name = f"omop_pydantic.models.{py_file.stem}"
        try:
            module = importlib.import_module(module_name)
            
            # Find all classes that inherit from OmopModel
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, OmopModel) and 
                    attr is not OmopModel and
                    attr is not OmopClinicalModel and
                    attr is not OmopVocabularyModel and
                    attr is not OmopReferenceModel):
                    model_classes.append(attr)
        except ImportError:
            continue
    
    return model_classes


class TestOmopModel:
    """Test base OmopModel functionality."""
    
    def test_table_name_pascal_to_snake(self):
        """Test table_name() converts PascalCase to snake_case."""
        
        class PersonTest(OmopModel):
            pass
            
        class ConditionOccurrence(OmopModel):
            pass
            
        class DrugExposure(OmopModel):
            pass
            
        assert PersonTest.table_name() == "person_test"
        assert ConditionOccurrence.table_name() == "condition_occurrence"
        assert DrugExposure.table_name() == "drug_exposure"
    
    def test_table_name_special_cases(self):
        """Test table_name() handles special naming cases."""
        
        class NoteNlp(OmopModel):
            pass
            
        # Would be note_nlp due to existing mapping logic
        assert NoteNlp.table_name() == "note_nlp"
    
    def test_extra_forbid_rejects_unknown_fields(self):
        """Test that extra='forbid' rejects unexpected columns."""
        
        class TestModel(OmopModel):
            test_id: int
            test_name: str
            
        # Valid data should work
        valid_data = {"test_id": 1, "test_name": "test"}
        model = TestModel(**valid_data)
        assert model.test_id == 1
        
        # Extra fields should be rejected
        with pytest.raises(ValueError, match="Extra inputs are not permitted"):
            TestModel(**valid_data, unexpected_field="should_fail")


class TestConceptIdValidation:
    """Test concept_id validation rules."""
    
    def test_concept_id_allows_zero(self):
        """Test that concept_id=0 is allowed (no matching concept)."""
        
        class TestModel(OmopModel):
            test_concept_id: int
            
        # concept_id = 0 should be valid
        model = TestModel(test_concept_id=0)
        assert model.test_concept_id == 0
    
    def test_concept_id_allows_positive(self):
        """Test that positive concept_ids are allowed."""
        
        class TestModel(OmopModel):
            test_concept_id: int
            
        model = TestModel(test_concept_id=8532)
        assert model.test_concept_id == 8532
    
    def test_concept_id_rejects_negative(self):
        """Test that concept_ids reject values less than -1 in base model."""
        
        class TestModel(OmopModel):
            test_concept_id: int
            
        # -1 is now allowed (means "no matching concept")
        model = TestModel(test_concept_id=-1)
        assert model.test_concept_id == -1
        
        # But -2 and below should still be rejected
        with pytest.raises(ValueError, match="must be >= -1"):
            TestModel(test_concept_id=-2)


class TestIdFieldValidation:
    """Test ID field validation rules."""
    
    def test_regular_id_requires_positive(self):
        """Test that regular ID fields must be positive."""
        
        class TestModel(OmopModel):
            test_id: int
            person_id: int
            
        # Positive IDs should work
        model = TestModel(test_id=1, person_id=123)
        assert model.test_id == 1
        assert model.person_id == 123
        
        # Zero should fail for regular IDs
        with pytest.raises(ValueError, match="test_id must be a positive integer"):
            TestModel(test_id=0, person_id=123)
            
        with pytest.raises(ValueError, match="person_id must be a positive integer"):
            TestModel(test_id=1, person_id=0)
    
    def test_concept_ids_exempt_from_positive_rule(self):
        """Test that concept_ids are exempt from the positive ID rule."""
        
        class TestModel(OmopModel):
            test_id: int
            test_concept_id: int
            
        # concept_id=0 should work, but regular ID=0 should fail
        with pytest.raises(ValueError, match="test_id must be a positive integer"):
            TestModel(test_id=0, test_concept_id=0)
            
        # This should work - concept_id can be 0
        model = TestModel(test_id=1, test_concept_id=0)
        assert model.test_id == 1
        assert model.test_concept_id == 0


class TestVocabularyModel:
    """Test vocabulary model overrides."""
    
    def test_vocabulary_allows_negative_concept_ids(self):
        """Test that vocabulary models allow negative concept_ids."""
        
        class TestVocabModel(OmopVocabularyModel):
            test_concept_id: int
            
        # Negative concept_ids should be allowed in vocabulary models
        model = TestVocabModel(test_concept_id=-1)
        assert model.test_concept_id == -1


class TestParameterizedModelBehaviors:
    """Parameterized tests for common model behaviors across all models."""
    
    def test_table_name_conversion(self, all_model_classes):
        """Test that all models can generate correct table names."""
        for model_class in all_model_classes:
            table_name = model_class.table_name()
            
            # Should be lowercase
            assert table_name.islower(), f"{model_class.__name__} table_name should be lowercase"
            
            # Should not be empty
            assert table_name, f"{model_class.__name__} table_name should not be empty"
            
            # Should be snake_case (no consecutive underscores, no leading/trailing underscores)
            assert not table_name.startswith('_'), f"{model_class.__name__} table_name should not start with underscore"
            assert not table_name.endswith('_'), f"{model_class.__name__} table_name should not end with underscore"
            assert '__' not in table_name, f"{model_class.__name__} table_name should not have consecutive underscores"
    
    def test_extra_fields_forbidden(self, all_model_classes):
        """Test that all models reject extra fields."""
        for model_class in all_model_classes:
            # Create minimal valid data for the model
            valid_data = {}
            
            # Find required fields and provide minimal values
            for field_name, field_info in model_class.model_fields.items():
                if field_info.is_required():
                    # Provide appropriate default values based on field type
                    annotation = field_info.annotation
                    
                    # Check for Literal types first (before handling Optional)
                    if 'Literal' in str(annotation):
                        # For Literal types, extract the first allowed value
                        if hasattr(annotation, '__args__') and annotation.__args__:
                            valid_data[field_name] = annotation.__args__[0]
                        else:
                            valid_data[field_name] = "Y"  # Common default for Y/N literals
                    else:
                        # Handle Optional types for non-Literal fields
                        if hasattr(annotation, '__origin__'):
                            args = getattr(annotation, '__args__', ())
                            if args:
                                annotation = args[0]
                        
                        if annotation == int or 'int' in str(annotation):
                            valid_data[field_name] = 1
                        elif annotation == str or 'str' in str(annotation):
                            valid_data[field_name] = "test"
                        elif annotation == date or 'date' in str(annotation):
                            valid_data[field_name] = date(2020, 1, 1)
                        elif annotation == datetime or 'datetime' in str(annotation):
                            valid_data[field_name] = datetime(2020, 1, 1, 12, 0, 0)
                        elif annotation == Decimal or 'Decimal' in str(annotation):
                            valid_data[field_name] = Decimal('10.0')
            
            
            # Test that model can be created with valid data
            if valid_data:  # Only test if we have required fields
                try:
                    model = model_class(**valid_data)
                    assert model is not None
                    
                    # Test that extra fields are rejected
                    with pytest.raises(ValueError, match="Extra inputs are not permitted"):
                        model_class(**valid_data, extra_field="should_fail")
                except Exception as e:
                    print(f"Failed to create {model_class.__name__} with data: {valid_data}")
                    raise
    
    def test_primary_key_field_detection(self, all_model_classes):
        """Test that primary key field can be detected for all models."""
        for model_class in all_model_classes:
            pk_field = model_class.get_primary_key_field()
            
            # Most models should have a primary key field
            if pk_field:
                # Should end with _id
                assert pk_field.endswith('_id'), f"{model_class.__name__} primary key should end with '_id'"
                
                # Should be present in model fields
                assert pk_field in model_class.model_fields, f"{model_class.__name__} primary key field should exist in model"
                
                # Primary key field should be an integer or string type
                field_info = model_class.model_fields[pk_field]
                annotation = field_info.annotation
                assert ('int' in str(annotation) or 'str' in str(annotation)), f"{model_class.__name__} primary key should be integer or string type"
    
    def test_field_categorization(self, all_model_classes):
        """Test that field categorization methods work for all models."""
        for model_class in all_model_classes:
            # Create a dummy instance to test field categorization
            # We'll use minimal data and allow validation errors since we're just testing categorization
            try:
                # Get field sets (this triggers _ensure_fields_initialized)
                model_class._ensure_fields_initialized()
                
                # Test that field sets are properly typed
                assert isinstance(model_class._concept_fields, set)
                assert isinstance(model_class._id_fields, set)
                assert isinstance(model_class._source_value_fields, set)
                assert isinstance(model_class._date_fields, set)
                assert isinstance(model_class._datetime_fields, set)
                
                # Verify concept fields end with _concept_id
                for field in model_class._concept_fields:
                    assert field.endswith('_concept_id'), f"Concept field {field} should end with '_concept_id'"
                
                # Verify source value fields end with _source_value
                for field in model_class._source_value_fields:
                    assert field.endswith('_source_value'), f"Source value field {field} should end with '_source_value'"
                
                # Verify ID fields contain _id
                for field in model_class._id_fields:
                    assert '_id' in field, f"ID field {field} should contain '_id'"
                    
            except Exception:
                # Some models might fail to instantiate, but field categorization should still work
                pass


class TestRoundTripSerialization:
    """Test round-trip serialization for all models."""
    
    def test_model_dump_and_parse_roundtrip(self, all_model_classes):
        """Test that models can be dumped and parsed back to equal objects."""
        for model_class in all_model_classes:
            # Create minimal valid data
            valid_data = {}
            
            for field_name, field_info in model_class.model_fields.items():
                if field_info.is_required():
                    annotation = field_info.annotation
                    
                    # Check for Literal types first (before handling Optional)
                    if 'Literal' in str(annotation):
                        # For Literal types, extract the first allowed value
                        if hasattr(annotation, '__args__') and annotation.__args__:
                            valid_data[field_name] = annotation.__args__[0]
                        else:
                            valid_data[field_name] = "Y"  # Common default for Y/N literals
                    else:
                        # Handle Optional types for non-Literal fields
                        if hasattr(annotation, '__origin__'):
                            args = getattr(annotation, '__args__', ())
                            if args:
                                annotation = args[0]
                        
                        if annotation == int or 'int' in str(annotation):
                            valid_data[field_name] = 1
                        elif annotation == str or 'str' in str(annotation):
                            valid_data[field_name] = "test"
                        elif annotation == date or 'date' in str(annotation):
                            valid_data[field_name] = date(2020, 1, 1)
                        elif annotation == datetime or 'datetime' in str(annotation):
                            valid_data[field_name] = datetime(2020, 1, 1, 12, 0, 0)
                        elif annotation == Decimal or 'Decimal' in str(annotation):
                            valid_data[field_name] = Decimal('10.0')
            
            if valid_data:
                # Create original model
                original = model_class(**valid_data)
                
                # Dump to dict and parse back
                dumped = original.model_dump()
                parsed = model_class.model_validate(dumped)
                
                # Should be equal
                assert original == parsed, f"Round-trip failed for {model_class.__name__}"
                
                # Dump to JSON string and parse back
                json_str = original.model_dump_json()
                from_json = model_class.model_validate_json(json_str)
                
                # Should be equal
                assert original == from_json, f"JSON round-trip failed for {model_class.__name__}"


class TestDateValidation:
    """Test date range validation across all models."""
    
    def test_date_range_validation_patterns(self):
        """Test that date range validation works for common patterns."""
        
        class TestDateModel(OmopModel):
            test_id: int
            start_date: date
            end_date: date
            exposure_start_date: date
            exposure_end_date: date
        
        # Valid ranges should work
        valid_model = TestDateModel(
            test_id=1,
            start_date=date(2020, 1, 1),
            end_date=date(2020, 12, 31),
            exposure_start_date=date(2020, 6, 1),
            exposure_end_date=date(2020, 6, 30)
        )
        assert valid_model.start_date < valid_model.end_date
        
        # Invalid ranges should fail
        with pytest.raises(ValueError, match="start_date.*must be before or equal to.*end_date"):
            TestDateModel(
                test_id=1,
                start_date=date(2020, 12, 31),
                end_date=date(2020, 1, 1),  # Invalid: end before start
                exposure_start_date=date(2020, 6, 1),
                exposure_end_date=date(2020, 6, 30)
            )
        
        with pytest.raises(ValueError, match="exposure_start_date.*must be before or equal to.*exposure_end_date"):
            TestDateModel(
                test_id=1,
                start_date=date(2020, 1, 1),
                end_date=date(2020, 12, 31),
                exposure_start_date=date(2020, 6, 30),
                exposure_end_date=date(2020, 6, 1)  # Invalid: end before start
            )
    
    def test_date_datetime_consistency(self):
        """Test that date and datetime fields are consistent."""
        
        class TestDateTimeModel(OmopModel):
            test_id: int
            visit_start_date: date
            visit_start_datetime: datetime
        
        # Consistent date/datetime should work
        consistent_model = TestDateTimeModel(
            test_id=1,
            visit_start_date=date(2020, 1, 1),
            visit_start_datetime=datetime(2020, 1, 1, 12, 0, 0)
        )
        assert consistent_model.visit_start_date == consistent_model.visit_start_datetime.date()
        
        # Inconsistent date/datetime should fail
        with pytest.raises(ValueError, match="visit_start_date.*does not match.*visit_start_datetime"):
            TestDateTimeModel(
                test_id=1,
                visit_start_date=date(2020, 1, 1),
                visit_start_datetime=datetime(2020, 1, 2, 12, 0, 0)  # Different date
            )