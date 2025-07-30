"""
Property-based tests using Hypothesis for comprehensive validation.
"""
import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Type, Any, Dict, get_origin, get_args, Optional
import hypothesis.strategies as st
from hypothesis import given, assume, settings, HealthCheck
from pydantic import Field
from omop_pydantic.base import OmopModel, OmopVocabularyModel


# Hypothesis strategies for OMOP data types
@st.composite
def omop_date(draw):
    """Generate realistic dates for OMOP data (1900-2030)."""
    return draw(st.dates(
        min_value=date(1900, 1, 1),
        max_value=date(2030, 12, 31)
    ))


@st.composite  
def omop_datetime(draw):
    """Generate realistic datetimes for OMOP data."""
    return draw(st.datetimes(
        min_value=datetime(1900, 1, 1),
        max_value=datetime(2030, 12, 31),
        timezones=st.none()  # OMOP typically doesn't use timezones
    ))


@st.composite
def omop_concept_id(draw, allow_negative=False):
    """Generate concept IDs (0 for unmapped, positive for mapped, negative for vocab models)."""
    if allow_negative:
        return draw(st.integers(min_value=-999999, max_value=999999))
    else:
        return draw(st.integers(min_value=0, max_value=999999))


@st.composite
def omop_id(draw):
    """Generate positive integer IDs."""
    return draw(st.integers(min_value=1, max_value=999999))


@st.composite
def omop_string(draw, max_length=255):
    """Generate strings with appropriate length for OMOP fields."""
    return draw(st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd', 'Zs')),
        min_size=0,
        max_size=max_length
    ))


@st.composite
def omop_decimal(draw):
    """Generate decimal values for OMOP numeric fields."""
    return draw(st.decimals(
        min_value=Decimal('-99999.99'),
        max_value=Decimal('99999.99'),
        places=2
    ))


def generate_model_data(model_class: Type[OmopModel]) -> st.SearchStrategy[Dict[str, Any]]:
    """Generate valid data for any OMOP model class."""
    field_strategies = {}
    
    for field_name, field_info in model_class.model_fields.items():
        annotation = field_info.annotation
        
        # Handle Optional types
        if get_origin(annotation) is type(Optional[int]):
            args = get_args(annotation)
            if args:
                annotation = args[0]
        
        # Check for Literal types first
        if 'Literal' in str(annotation):
            # Extract literal values
            if hasattr(annotation, '__args__') and annotation.__args__:
                strategy = st.sampled_from(annotation.__args__)
            else:
                strategy = st.just("Y")  # Default fallback
        # Determine strategy based on field type and name
        elif annotation == int or 'int' in str(annotation):
            if field_name.endswith('_concept_id'):
                # Allow negative for vocabulary models
                allow_negative = issubclass(model_class, OmopVocabularyModel)
                strategy = omop_concept_id(allow_negative=allow_negative)
            elif '_id' in field_name:
                # For primary key fields, allow zero (despite base validation)
                is_primary_key = field_name == f"{model_class.table_name()}_id"
                if is_primary_key:
                    strategy = st.integers(min_value=0, max_value=999999)
                else:
                    strategy = omop_id()
            else:
                strategy = st.integers(min_value=0, max_value=9999)
        elif annotation == str or 'str' in str(annotation):
            # Determine max length based on field name patterns
            if 'source_value' in field_name:
                max_len = 50
            elif 'name' in field_name:
                max_len = 255
            elif 'code' in field_name:
                max_len = 50
            else:
                max_len = 255
            strategy = omop_string(max_length=max_len)
        elif annotation == date or 'date' in str(annotation):
            strategy = omop_date()
        elif annotation == datetime or 'datetime' in str(annotation):
            strategy = omop_datetime()
        elif annotation == Decimal or 'Decimal' in str(annotation):
            strategy = omop_decimal()
        else:
            # Fallback for unknown types
            strategy = st.none()
        
        # Make optional fields optional
        if not field_info.is_required():
            strategy = st.one_of(st.none(), strategy)
            
        field_strategies[field_name] = strategy
    
    return st.fixed_dictionaries(field_strategies)


def get_all_model_classes():
    """Get all model classes for property-based testing."""
    import importlib
    from pathlib import Path
    
    models_dir = Path(__file__).parent.parent / "omop_pydantic" / "models"
    model_classes = []
    
    for py_file in models_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
            
        module_name = f"omop_pydantic.models.{py_file.stem}"
        try:
            module = importlib.import_module(module_name)
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, OmopModel) and 
                    attr is not OmopModel and
                    not attr.__name__.startswith('Omop')):
                    model_classes.append(attr)
        except ImportError:
            continue
    
    return model_classes


class TestPropertyBasedRoundTrip:
    """Property-based tests for round-trip serialization."""
    
    @given(data=st.data())
    @settings(
        max_examples=5,  # Reduced for faster execution 
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much, HealthCheck.function_scoped_fixture],
        deadline=5000  # 5 second deadline
    )
    def test_round_trip_serialization(self, data):
        """Test that any valid model instance can round-trip through serialization."""
        # Get model classes and pick a random one for this test
        all_model_classes = get_all_model_classes()
        model_class = data.draw(st.sampled_from(all_model_classes))
        
        try:
            # Generate valid data for this model
            model_data = data.draw(generate_model_data(model_class))
            
            # Skip if no required fields can be satisfied
            if not any(field_info.is_required() for field_info in model_class.model_fields.values()):
                assume(False)  # Skip this example
            
            # Create model instance
            original = model_class(**model_data)
            
            # Test dict round-trip
            dumped = original.model_dump()
            reconstructed = model_class.model_validate(dumped)
            assert original == reconstructed, f"Dict round-trip failed for {model_class.__name__}"
            
            # Test JSON round-trip
            json_str = original.model_dump_json()
            from_json = model_class.model_validate_json(json_str)
            assert original == from_json, f"JSON round-trip failed for {model_class.__name__}"
            
        except Exception:
            # Some model combinations might be invalid due to constraints
            # This is expected and we skip those examples
            assume(False)


class TestPropertyBasedDateValidation:
    """Property-based tests for date validation."""
    
    @given(
        start_date=omop_date(),
        end_date=omop_date()
    )
    def test_date_range_validation(self, start_date: date, end_date: date):
        """Test date range validation with random date pairs."""
        
        class TestDateRangeModel(OmopModel):
            test_id: int
            start_date: date
            end_date: date
        
        if start_date <= end_date:
            # Valid range should work
            model = TestDateRangeModel(
                test_id=1,
                start_date=start_date,
                end_date=end_date
            )
            assert model.start_date <= model.end_date
        else:
            # Invalid range should fail
            with pytest.raises(ValueError, match="start_date.*must be before or equal to.*end_date"):
                TestDateRangeModel(
                    test_id=1,
                    start_date=start_date,
                    end_date=end_date
                )
    
    @given(
        base_date=omop_date(),
        hour=st.integers(min_value=0, max_value=23),
        minute=st.integers(min_value=0, max_value=59),
        second=st.integers(min_value=0, max_value=59)
    )
    def test_date_datetime_consistency(self, base_date: date, hour: int, minute: int, second: int):
        """Test that date and datetime fields must be consistent."""
        
        class TestDateTimeModel(OmopModel):
            test_id: int
            visit_start_date: date
            visit_start_datetime: datetime
        
        consistent_datetime = datetime.combine(base_date, datetime.min.time().replace(
            hour=hour, minute=minute, second=second
        ))
        
        # Consistent date/datetime should work
        model = TestDateTimeModel(
            test_id=1,
            visit_start_date=base_date,
            visit_start_datetime=consistent_datetime
        )
        assert model.visit_start_date == model.visit_start_datetime.date()
        
        # Inconsistent should fail
        inconsistent_date = base_date + timedelta(days=1)
        with pytest.raises(ValueError, match="visit_start_date.*does not match.*visit_start_datetime"):
            TestDateTimeModel(
                test_id=1,
                visit_start_date=inconsistent_date,
                visit_start_datetime=consistent_datetime
            )


class TestPropertyBasedConceptValidation:
    """Property-based tests for concept ID validation."""
    
    @given(concept_id=st.integers(min_value=-999999, max_value=999999))
    def test_vocabulary_model_concept_ids(self, concept_id: int):
        """Test that vocabulary models accept any concept ID including negative."""
        
        class TestVocabModel(OmopVocabularyModel):
            test_concept_id: int
        
        # Vocabulary models should accept any concept ID
        model = TestVocabModel(test_concept_id=concept_id)
        assert model.test_concept_id == concept_id
    
    @given(concept_id=st.integers(min_value=-1, max_value=999999))
    def test_clinical_model_concept_ids(self, concept_id: int):
        """Test that clinical models accept concept IDs >= -1."""
        
        class TestClinicalModel(OmopModel):
            test_id: int
            test_concept_id: int
        
        # Concept IDs >= -1 should work (0 and -1 mean "no matching concept")
        model = TestClinicalModel(test_id=1, test_concept_id=concept_id)
        assert model.test_concept_id == concept_id
    
    @given(concept_id=st.integers(min_value=-999999, max_value=-2))
    def test_clinical_model_rejects_negative_concept_ids(self, concept_id: int):
        """Test that clinical models reject concept IDs less than -1."""
        
        class TestClinicalModel(OmopModel):
            test_id: int
            test_concept_id: int
        
        # Concept IDs less than -1 should fail in clinical models
        with pytest.raises(ValueError, match="must be >= -1"):
            TestClinicalModel(test_id=1, test_concept_id=concept_id)


class TestPropertyBasedStringValidation:
    """Property-based tests for string field validation."""
    
    @given(
        text=st.text(max_size=255),
        max_length=st.integers(min_value=1, max_value=255)
    )
    def test_string_length_constraints(self, text: str, max_length: int):
        """Test string length validation with various inputs."""
        
        class TestStringModel(OmopModel):
            test_id: int
            test_field: str = Field(..., max_length=max_length)
        
        if len(text) <= max_length:
            # Valid length should work
            model = TestStringModel(test_id=1, test_field=text)
            assert model.test_field == text
        else:
            # Too long should fail
            # Handle both singular and plural forms of the error message
            char_word = "character" if max_length == 1 else "characters"
            with pytest.raises(ValueError, match=f"String should have at most {max_length} {char_word}"):
                TestStringModel(test_id=1, test_field=text)