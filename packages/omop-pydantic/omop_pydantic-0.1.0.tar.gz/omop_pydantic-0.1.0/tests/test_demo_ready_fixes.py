"""
Tests for demo-ready fixes to omop-pydantic.
"""
import pytest
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Union

from omop_pydantic.base import OmopModel, OmopClinicalModel
from omop_pydantic.models.measurement import Measurement
from omop_pydantic.models.observation import Observation
from omop_pydantic.models.procedure_occurrence import ProcedureOccurrence


class TestOptionalFieldDetection:
    """Test fixes for optional field detection."""
    
    def test_optional_date_remains_none(self):
        """Test that Optional[date] fields can remain None without error."""
        
        class TestModel(OmopModel):
            test_id: int
            optional_date: Optional[date] = None
            
        # Should work fine with None
        model = TestModel(test_id=1, optional_date=None)
        assert model.optional_date is None
        
        # Should also work with a value
        model2 = TestModel(test_id=1, optional_date=date(2020, 1, 1))
        assert model2.optional_date == date(2020, 1, 1)
    
    def test_optional_datetime_remains_none(self):
        """Test that Optional[datetime] fields can remain None without error."""
        
        class TestModel(OmopModel):
            test_id: int
            optional_datetime: Optional[datetime] = None
            
        # Should work fine with None
        model = TestModel(test_id=1, optional_datetime=None)
        assert model.optional_datetime is None
    
    def test_union_type_detection(self):
        """Test that Union[X, None] types are properly detected."""
        
        class TestModel(OmopModel):
            test_id: int
            union_field: Union[str, None] = None
            
        # Should work fine
        model = TestModel(test_id=1, union_field=None)
        assert model.union_field is None
        
        model2 = TestModel(test_id=1, union_field="test")
        assert model2.union_field == "test"
    
    def test_required_field_raises_error(self):
        """Test that non-optional fields still raise errors when None."""
        
        class TestModel(OmopModel):
            test_id: int
            required_date: date
            
        # Should raise error for missing required field
        with pytest.raises(ValueError):
            TestModel(test_id=1)


class TestConceptIdValidation:
    """Test loosened ID validation rules for concept fields."""
    
    def test_concept_id_allows_zero(self):
        """Test that concept_id fields can be 0 (no matching concept)."""
        
        class TestModel(OmopModel):
            procedure_concept_id: int
            
        model = TestModel(procedure_concept_id=0)
        assert model.procedure_concept_id == 0
    
    def test_concept_id_allows_negative_one(self):
        """Test that concept_id fields can be -1 (no matching concept)."""
        
        class TestModel(OmopModel):
            drug_concept_id: int
            
        model = TestModel(drug_concept_id=-1)
        assert model.drug_concept_id == -1
    
    def test_source_concept_id_allows_zero(self):
        """Test that source_concept_id fields can be 0."""
        
        class TestModel(OmopModel):
            procedure_source_concept_id: int
            
        model = TestModel(procedure_source_concept_id=0)
        assert model.procedure_source_concept_id == 0
    
    def test_regular_id_still_requires_positive(self):
        """Test that regular ID fields still require positive values."""
        
        class TestModel(OmopModel):
            person_id: int
            provider_id: int
            
        # Should work with positive values
        model = TestModel(person_id=1, provider_id=2)
        assert model.person_id == 1
        
        # Should fail with zero
        with pytest.raises(ValueError, match="person_id must be a positive integer"):
            TestModel(person_id=0, provider_id=1)
        
        # Should fail with negative
        with pytest.raises(ValueError, match="provider_id must be a positive integer"):
            TestModel(person_id=1, provider_id=-1)


class TestDecimalPrecision:
    """Test Decimal precision preservation in JSON."""
    
    def test_decimal_serializes_as_string(self):
        """Test that Decimal values serialize to exact string representation."""
        
        class TestModel(OmopModel):
            test_id: int
            exact_value: Decimal
            
        model = TestModel(test_id=1, exact_value=Decimal("19.99"))
        
        # Test JSON serialization
        json_str = model.model_dump_json()
        assert '"exact_value":"19.99"' in json_str or '"exact_value": "19.99"' in json_str
        
        # Should NOT contain float representation
        assert "19.989999" not in json_str
        assert "19.99000" not in json_str
    
    def test_decimal_precision_roundtrip(self):
        """Test that Decimal precision is preserved in round-trip serialization."""
        
        class TestModel(OmopModel):
            test_id: int
            price: Decimal
            
        original = TestModel(test_id=1, price=Decimal("0.1"))
        
        # Serialize and deserialize
        json_str = original.model_dump_json()
        restored = TestModel.model_validate_json(json_str)
        
        # Should maintain exact precision
        assert restored.price == Decimal("0.1")
        assert str(restored.price) == "0.1"
    
    def test_decimal_none_handling(self):
        """Test that None Decimal values are handled correctly."""
        
        class TestModel(OmopModel):
            test_id: int
            optional_decimal: Optional[Decimal] = None
            
        model = TestModel(test_id=1, optional_decimal=None)
        json_str = model.model_dump_json()
        assert '"optional_decimal":null' in json_str or '"optional_decimal": null' in json_str
    
    def test_decimal_zero_serialization(self):
        """Test that Decimal(0) serializes to '0' not None."""
        
        class TestModel(OmopModel):
            test_id: int
            exact_value: Decimal
            
        model = TestModel(test_id=1, exact_value=Decimal("0"))
        
        # Test JSON serialization
        json_str = model.model_dump_json()
        assert '"exact_value":"0"' in json_str
        
        # Should NOT be null
        assert '"exact_value":null' not in json_str
        assert '"exact_value": null' not in json_str


class TestMeasurementObservation54Fields:
    """Test OMOP CDM 5.4 fields in Measurement and Observation."""
    
    def test_measurement_54_fields_present(self):
        """Test that Measurement has 5.4 linking fields."""
        # Fields should be in model_fields
        assert 'measurement_event_id' in Measurement.model_fields
        assert 'meas_event_field_concept_id' in Measurement.model_fields
        
        # Check field types
        assert Measurement.model_fields['measurement_event_id'].annotation == Optional[int]
        assert Measurement.model_fields['meas_event_field_concept_id'].annotation == Optional[int]
    
    def test_observation_54_fields_present(self):
        """Test that Observation has 5.4 linking fields."""
        # Fields should be in model_fields
        assert 'observation_event_id' in Observation.model_fields
        assert 'obs_event_field_concept_id' in Observation.model_fields
        
        # Check field types
        assert Observation.model_fields['observation_event_id'].annotation == Optional[int]
        assert Observation.model_fields['obs_event_field_concept_id'].annotation == Optional[int]
    
    def test_measurement_backward_compatibility(self):
        """Test that Measurement can load 5.3 data without new fields."""
        # Minimal 5.3 data without the new fields
        data_53 = {
            'measurement_id': 1,
            'person_id': 100,
            'measurement_concept_id': 3000963,
            'measurement_date': date(2020, 1, 1),
            'measurement_type_concept_id': 44818702
        }
        
        # Should load without error
        measurement = Measurement(**data_53)
        assert measurement.measurement_id == 1
        assert measurement.measurement_event_id is None
        assert measurement.meas_event_field_concept_id is None
    
    def test_observation_backward_compatibility(self):
        """Test that Observation can load 5.3 data without new fields."""
        # Minimal 5.3 data without the new fields
        data_53 = {
            'observation_id': 1,
            'person_id': 100,
            'observation_concept_id': 4005823,
            'observation_date': date(2020, 1, 1),
            'observation_type_concept_id': 38000280
        }
        
        # Should load without error
        observation = Observation(**data_53)
        assert observation.observation_id == 1
        assert observation.observation_event_id is None
        assert observation.obs_event_field_concept_id is None
    
    def test_measurement_with_54_fields(self):
        """Test Measurement with 5.4 fields populated."""
        data_54 = {
            'measurement_id': 1,
            'person_id': 100,
            'measurement_concept_id': 3000963,
            'measurement_date': date(2020, 1, 1),
            'measurement_type_concept_id': 44818702,
            'measurement_event_id': 5000,
            'meas_event_field_concept_id': 1147306
        }
        
        measurement = Measurement(**data_54)
        assert measurement.measurement_event_id == 5000
        assert measurement.meas_event_field_concept_id == 1147306


class TestCaseInsensitiveLoading:
    """Test case insensitive field loading for CSV compatibility."""
    
    def test_case_insensitive_validation_method_exists(self):
        """Test that case-insensitive validation method exists."""
        from omop_pydantic.base import OmopModel
        
        # Check that the method exists
        assert hasattr(OmopModel, 'model_validate_case_insensitive')
    
    def test_upper_snake_case_loading(self):
        """Test loading data with UPPER_SNAKE_CASE field names."""
        
        class TestModel(OmopModel):
            person_id: int
            procedure_concept_id: int
            procedure_date: date
            
        # Data with UPPER_SNAKE_CASE keys
        upper_data = {
            'PERSON_ID': 100,
            'PROCEDURE_CONCEPT_ID': 4013772,
            'PROCEDURE_DATE': date(2020, 1, 1)
        }
        
        # Should load successfully using case-insensitive method
        model = TestModel.model_validate_case_insensitive(upper_data)
        assert model.person_id == 100
        assert model.procedure_concept_id == 4013772
        assert model.procedure_date == date(2020, 1, 1)
    
    def test_mixed_case_loading(self):
        """Test loading with mixed case field names."""
        
        class TestModel(OmopModel):
            test_id: int
            test_name: str
            
        # Test various case combinations
        test_cases = [
            {'TEST_ID': 1, 'TEST_NAME': 'upper'},
            {'test_id': 2, 'test_name': 'lower'},
            {'Test_Id': 3, 'Test_Name': 'mixed'},
        ]
        
        for data in test_cases:
            model = TestModel.model_validate_case_insensitive(data)
            assert model.test_id in [1, 2, 3]
            assert model.test_name in ['upper', 'lower', 'mixed']
    
    def test_model_dump_uses_lowercase(self):
        """Test that model_dump() returns lowercase keys."""
        
        class TestModel(OmopModel):
            person_id: int
            visit_occurrence_id: int
            
        model = TestModel(person_id=100, visit_occurrence_id=200)
        dumped = model.model_dump()
        
        # Keys should be lowercase
        assert 'person_id' in dumped
        assert 'visit_occurrence_id' in dumped
        assert 'PERSON_ID' not in dumped
        assert 'VISIT_OCCURRENCE_ID' not in dumped


class TestCompositePrimaryKey:
    """Test composite primary key helper method."""
    
    def test_single_primary_key_detection(self):
        """Test primary_key_fields() for models with single PK."""
        # ProcedureOccurrence should have procedure_occurrence_id
        pk_fields = ProcedureOccurrence.primary_key_fields()
        assert pk_fields == ('procedure_occurrence_id',)
    
    def test_primary_key_fields_empty_for_no_pk(self):
        """Test primary_key_fields() returns empty tuple when no PK found."""
        
        class NoPkModel(OmopModel):
            some_field: str
            another_field: int
            
        pk_fields = NoPkModel.primary_key_fields()
        assert pk_fields == ()
    
    def test_composite_pk_with_json_schema_extra(self):
        """Test composite PK detection using json_schema_extra."""
        from pydantic import Field
        
        class CompositePkModel(OmopModel):
            drug_cost_id: int = Field(json_schema_extra={'pk': True})
            ingredient_cost_id: int = Field(json_schema_extra={'pk': True})
            amount: Decimal
            
        pk_fields = CompositePkModel.primary_key_fields()
        assert set(pk_fields) == {'drug_cost_id', 'ingredient_cost_id'}
    
    def test_primary_key_fields_without_json_schema_extra(self):
        """Test that primary_key_fields handles fields without json_schema_extra."""
        
        class TestModel(OmopModel):
            test_model_id: int  # Matches table_name + '_id' pattern
            regular_field: str
            another_field: Optional[int] = None
            
        # Should not raise AttributeError
        pk_fields = TestModel.primary_key_fields()
        
        # Should find the standard pattern
        assert pk_fields == ('test_model_id',)
    
    def test_explicit_primary_key_attribute(self):
        """Test using explicit _primary_key attribute."""
        
        class ExplicitPkModel(OmopModel):
            _primary_key = 'custom_id'  # Simple class attribute
            custom_id: int
            other_field: str
            
        pk_fields = ExplicitPkModel.primary_key_fields()
        assert pk_fields == ('custom_id',)


class TestUpperCaseOutput:
    """Test UPPER_SNAKE_CASE output functionality."""
    
    def test_model_dump_upper_method_exists(self):
        """Test that model_dump_upper method exists."""
        from omop_pydantic.base import OmopModel
        
        assert hasattr(OmopModel, 'model_dump_upper')
    
    def test_model_dump_upper_converts_keys(self):
        """Test that model_dump_upper converts keys to uppercase."""
        
        class TestModel(OmopModel):
            person_id: int
            procedure_concept_id: int
            procedure_date: date
            
        model = TestModel(
            person_id=100,
            procedure_concept_id=4013772,
            procedure_date=date(2020, 1, 1)
        )
        
        upper_data = model.model_dump_upper()
        
        # Check keys are uppercase
        assert 'PERSON_ID' in upper_data
        assert 'PROCEDURE_CONCEPT_ID' in upper_data
        assert 'PROCEDURE_DATE' in upper_data
        
        # Check lowercase keys are not present
        assert 'person_id' not in upper_data
        assert 'procedure_concept_id' not in upper_data
        
        # Check values are preserved
        assert upper_data['PERSON_ID'] == 100
        assert upper_data['PROCEDURE_CONCEPT_ID'] == 4013772
    
    def test_round_trip_with_upper_case(self):
        """Test round-trip serialization with uppercase keys."""
        
        class TestModel(OmopModel):
            test_id: int
            test_name: str
            test_value: Decimal
            
        original = TestModel(test_id=1, test_name="test", test_value=Decimal("123.45"))
        
        # Dump to uppercase
        upper_data = original.model_dump_upper()
        
        # Load back using case-insensitive method
        restored = TestModel.model_validate_case_insensitive(upper_data)
        
        # Should be equal
        assert restored == original
        assert restored.test_id == 1
        assert restored.test_name == "test"
        assert restored.test_value == Decimal("123.45")


class TestDateRangeRegex:
    """Test regex-based date range validation."""
    
    def test_dose_era_dates_validated(self):
        """Test that DOSE_ERA start/end dates are validated."""
        
        class DoseEra(OmopModel):
            dose_era_id: int
            person_id: int
            drug_concept_id: int
            unit_concept_id: int
            dose_value: Decimal
            dose_era_start_date: date
            dose_era_end_date: date
            
        # Valid range
        valid = DoseEra(
            dose_era_id=1,
            person_id=100,
            drug_concept_id=1234,
            unit_concept_id=8718,
            dose_value=Decimal("50"),
            dose_era_start_date=date(2020, 1, 1),
            dose_era_end_date=date(2020, 12, 31)
        )
        assert valid.dose_era_start_date <= valid.dose_era_end_date
        
        # Invalid range
        with pytest.raises(ValueError, match="dose_era_start_date.*must be before or equal to.*dose_era_end_date"):
            DoseEra(
                dose_era_id=1,
                person_id=100,
                drug_concept_id=1234,
                unit_concept_id=8718,
                dose_value=Decimal("50"),
                dose_era_start_date=date(2020, 12, 31),
                dose_era_end_date=date(2020, 1, 1)
            )
    
    def test_various_prefix_patterns(self):
        """Test date range validation with various prefixes."""
        
        class TestModel(OmopModel):
            test_id: int
            # Standard pattern
            visit_start_date: date
            visit_end_date: date
            # With detail
            visit_detail_start_datetime: datetime
            visit_detail_end_datetime: datetime
            # Custom prefix
            custom_period_start_date: date
            custom_period_end_date: date
            
        # All valid ranges
        valid = TestModel(
            test_id=1,
            visit_start_date=date(2020, 1, 1),
            visit_end_date=date(2020, 1, 31),
            visit_detail_start_datetime=datetime(2020, 1, 1, 8, 0),
            visit_detail_end_datetime=datetime(2020, 1, 1, 17, 0),
            custom_period_start_date=date(2020, 1, 1),
            custom_period_end_date=date(2020, 12, 31)
        )
        assert valid.test_id == 1
        
        # Test each invalid range
        with pytest.raises(ValueError, match="visit_start_date.*must be before or equal to.*visit_end_date"):
            TestModel(
                test_id=1,
                visit_start_date=date(2020, 2, 1),
                visit_end_date=date(2020, 1, 1),
                visit_detail_start_datetime=datetime(2020, 1, 1, 8, 0),
                visit_detail_end_datetime=datetime(2020, 1, 1, 17, 0),
                custom_period_start_date=date(2020, 1, 1),
                custom_period_end_date=date(2020, 12, 31)
            )


class TestOptionalPrimitives:
    """Test optional primitive types work correctly."""
    
    def test_optional_int_none_allowed(self):
        """Test Optional[int] fields can be None."""
        
        class TestModel(OmopModel):
            test_id: int
            optional_int: Optional[int] = None
            
        model = TestModel(test_id=1, optional_int=None)
        assert model.optional_int is None
        
        # Can also have a value
        model2 = TestModel(test_id=1, optional_int=42)
        assert model2.optional_int == 42
    
    def test_optional_str_none_allowed(self):
        """Test Optional[str] fields can be None."""
        
        class TestModel(OmopModel):
            test_id: int
            optional_str: Optional[str] = None
            
        model = TestModel(test_id=1, optional_str=None)
        assert model.optional_str is None
        
        # Can also have a value
        model2 = TestModel(test_id=1, optional_str="test")
        assert model2.optional_str == "test"
    
    def test_optional_fields_in_json(self):
        """Test optional fields serialize correctly to JSON."""
        
        class TestModel(OmopModel):
            test_id: int
            optional_int: Optional[int] = None
            optional_str: Optional[str] = None
            optional_decimal: Optional[Decimal] = None
            
        # All None
        model1 = TestModel(test_id=1)
        json1 = model1.model_dump_json()
        assert '"optional_int":null' in json1 or '"optional_int": null' in json1
        
        # Mixed values
        model2 = TestModel(
            test_id=2,
            optional_int=42,
            optional_str=None,
            optional_decimal=Decimal("99.99")
        )
        json2 = model2.model_dump_json()
        assert '"optional_int":42' in json2
        assert '"optional_decimal":"99.99"' in json2


class TestRealWorldScenarios:
    """Integration tests for real-world usage scenarios."""
    
    def test_procedure_with_zero_source_concept(self):
        """Test creating a procedure with source_concept_id = 0."""
        data = {
            'procedure_occurrence_id': 1,
            'person_id': 100,
            'procedure_concept_id': 4013772,
            'procedure_date': date(2020, 1, 1),
            'procedure_datetime': datetime(2020, 1, 1, 10, 30),
            'procedure_type_concept_id': 38000275,
            'procedure_source_concept_id': 0  # No matching concept
        }
        
        # Should work without validation error
        procedure = ProcedureOccurrence(**data)
        assert procedure.procedure_source_concept_id == 0
    
    def test_measurement_with_decimal_values(self):
        """Test measurement with exact decimal values."""
        data = {
            'measurement_id': 1,
            'person_id': 100,
            'measurement_concept_id': 3004249,  # Serum creatinine
            'measurement_date': date(2020, 1, 1),
            'measurement_type_concept_id': 44818702,
            'value_as_number': Decimal('1.23'),
            'range_low': Decimal('0.50'),
            'range_high': Decimal('1.20')
        }
        
        measurement = Measurement(**data)
        
        # Check JSON serialization preserves precision
        json_str = measurement.model_dump_json()
        assert '"value_as_number":"1.23"' in json_str or '"value_as_number": "1.23"' in json_str
        assert '"range_low":"0.50"' in json_str or '"range_low": "0.50"' in json_str
        
        # Verify no float conversion artifacts
        assert '1.229999' not in json_str
        assert '0.5000' not in json_str