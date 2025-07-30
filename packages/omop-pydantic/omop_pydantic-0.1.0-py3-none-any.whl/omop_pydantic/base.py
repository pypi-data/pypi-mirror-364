from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, Optional, Set, ClassVar, get_args, get_origin, Union
import re
from pydantic import BaseModel, ConfigDict, model_validator, field_serializer, field_validator


class OmopModel(BaseModel):
    """
    Base model for all OMOP CDM tables.
    
    Provides common configuration for OMOP models.
    Use the more specific subclasses for different table types:
    - OmopClinicalModel: For clinical event tables with person_id
    - OmopVocabularyModel: For vocabulary reference tables
    - OmopReferenceModel: For other reference/lookup tables
    """
    
    model_config = ConfigDict(
        # Validate on assignment to ensure data integrity
        validate_assignment=True,
        # Use Enums by value for better serialization
        use_enum_values=True,
        # Allow arbitrary types for Decimal support
        arbitrary_types_allowed=True,
        # Populate by field name (allows exact field name matching)
        populate_by_name=True,
        # Reject unexpected columns
        extra="forbid",
    )

    # Pydantic V2 field serializers (replaces deprecated json_encoders)
    @field_serializer('*', when_used='json')
    def serialize_special_types(self, value: Any, field_name: str) -> Any:
        """
        Custom serializer for datetime, date, and Decimal fields.
        This replaces the deprecated json_encoders configuration.
        """
        if isinstance(value, datetime):
            return value.isoformat() if value else None
        elif isinstance(value, date):
            return value.isoformat() if value else None
        elif isinstance(value, Decimal):
            return str(value) if value is not None else None  # Preserve Decimal precision
        return value

    # Field validators for OMOP-specific rules
    @field_validator('*')
    @classmethod
    def validate_omop_fields(cls, v: Any, info) -> Any:
        """
        Comprehensive validator for OMOP field rules.
        Handles concept_id and ID field validation with special cases.
        """
        field_name = info.field_name
        if not field_name or not isinstance(v, int):
            return v
            
        # Check if this is a vocabulary model by checking the class name/MRO
        # We'll check if 'Vocabulary' is in the class name to avoid circular imports
        is_vocabulary_model = any('Vocabulary' in base.__name__ for base in cls.__mro__)
        
        # Concept ID validation - allow 0 and -1 for "no matching concept"
        if field_name.endswith('_concept_id') or field_name.endswith('_source_concept_id'):
            if v in (0, -1):
                return v  # Allow 0 and -1 for concept fields
            if not is_vocabulary_model and v < -1:
                raise ValueError(f"{field_name} must be >= -1 (concept IDs can be 0 or -1 for 'no matching concept')")
            return v
            
        # Regular ID field validation (non-concept IDs)
        # Only validate integer ID fields, not string IDs
        if '_id' in field_name and v <= 0:
            raise ValueError(f"{field_name} must be a positive integer")
            
        return v

    # Class-level attributes for OMOP semantics
    _concept_fields: ClassVar[Set[str]] = set()
    _source_value_fields: ClassVar[Set[str]] = set()
    _id_fields: ClassVar[Set[str]] = set()
    _date_fields: ClassVar[Set[str]] = set()
    _datetime_fields: ClassVar[Set[str]] = set()
    
    def __init_subclass__(cls, **kwargs):
        """
        Automatically identify OMOP field types when subclass is created.
        """
        super().__init_subclass__(**kwargs)
        
        # Reset field sets for each subclass
        cls._concept_fields = set()
        cls._source_value_fields = set()
        cls._id_fields = set()
        cls._date_fields = set()
        cls._datetime_fields = set()
    
    @model_validator(mode='after')
    def validate_date_datetime_consistency(self) -> 'OmopModel':
        """
        Ensure date and datetime fields are consistent.
        If both exist (e.g., visit_start_date and visit_start_datetime),
        the date should match the date portion of datetime.
        """
        # Ensure fields are initialized
        self._ensure_fields_initialized()
        
        for field_name in self._date_fields:
            # Check if there's a corresponding datetime field
            datetime_field = field_name.replace('_date', '_datetime')
            if datetime_field in self._datetime_fields:
                date_value = getattr(self, field_name, None)
                datetime_value = getattr(self, datetime_field, None)
                
                if date_value and datetime_value:
                    if date_value != datetime_value.date():
                        raise ValueError(
                            f"{field_name} ({date_value}) does not match "
                            f"date portion of {datetime_field} ({datetime_value.date()})"
                        )
        
        return self
    
    @model_validator(mode='after')
    def validate_date_ranges(self) -> 'OmopModel':
        """
        Validate that start dates/times are before or equal to end dates/times.
        Uses regex to match any field ending with _start_date(time) pattern.
        """
        # Pattern to match start date/datetime fields
        start_pattern = re.compile(r'^(.*)_start_(date|datetime)$')
        
        for field_name in self.__class__.model_fields:
            match = start_pattern.match(field_name)
            if match:
                # Extract prefix and suffix (date or datetime)
                prefix = match.group(1)
                suffix = match.group(2)
                
                # Construct the corresponding end field name
                end_field_name = f"{prefix}_end_{suffix}"
                
                if end_field_name in self.__class__.model_fields:
                    start_value = getattr(self, field_name, None)
                    end_value = getattr(self, end_field_name, None)
                    
                    if start_value and end_value:
                        if start_value > end_value:
                            raise ValueError(
                                f"{field_name} ({start_value}) must be before or equal to "
                                f"{end_field_name} ({end_value})"
                            )
        
        return self
    
    def get_concept_fields(self) -> Dict[str, Optional[int]]:
        """
        Return all concept fields and their values.
        """
        # Ensure fields are initialized
        self._ensure_fields_initialized()
        
        return {
            field: getattr(self, field, None)
            for field in self._concept_fields
            if hasattr(self, field)
        }
    
    @classmethod
    def _ensure_fields_initialized(cls):
        """
        Ensure field sets are populated. Called lazily on first access.
        """
        if not cls._concept_fields and not cls._id_fields and not cls._source_value_fields:
            # Analyze model fields
            for field_name, field_info in cls.model_fields.items():
                # Concept fields (fields ending with _concept_id)
                if field_name.endswith('_concept_id'):
                    cls._concept_fields.add(field_name)
                    # Also add to ID fields since concept_id fields are IDs too
                    cls._id_fields.add(field_name)
                # Source value fields
                elif field_name.endswith('_source_value'):
                    cls._source_value_fields.add(field_name)
                # ID fields (any field containing '_id' in the name)
                elif '_id' in field_name:
                    cls._id_fields.add(field_name)
                
                # Check annotation for date/datetime fields
                annotation = field_info.annotation
                
                # Handle Optional types (Union[X, None])
                if get_origin(annotation) is Union:
                    args = get_args(annotation)
                    if type(None) in args:
                        # Get the non-None type
                        annotation = next((arg for arg in args if arg is not type(None)), annotation)
                
                # Date/datetime fields
                if annotation is date:
                    cls._date_fields.add(field_name)
                elif annotation is datetime:
                    cls._datetime_fields.add(field_name)
    
    def get_source_values(self) -> Dict[str, Optional[str]]:
        """
        Return all source value fields and their values.
        """
        # Ensure fields are initialized
        self._ensure_fields_initialized()
        
        return {
            field: getattr(self, field, None)
            for field in self._source_value_fields
            if hasattr(self, field)
        }
    
    def get_source_value_fields(self) -> Dict[str, Optional[str]]:
        """
        Alias for get_source_values() for compatibility.
        """
        return self.get_source_values()
    
    def get_id_fields(self) -> Dict[str, Optional[int]]:
        """
        Return all ID fields and their values.
        """
        # Ensure fields are initialized
        self._ensure_fields_initialized()
        
        return {
            field: getattr(self, field, None)
            for field in self._id_fields
            if hasattr(self, field)
        }
    
    def get_temporal_fields(self) -> Dict[str, Optional[Any]]:
        """
        Return all date and datetime fields and their values.
        """
        # Ensure fields are initialized
        self._ensure_fields_initialized()
        
        temporal_fields = {}
        
        for field in self._date_fields:
            if hasattr(self, field):
                temporal_fields[field] = getattr(self, field, None)
                
        for field in self._datetime_fields:
            if hasattr(self, field):
                temporal_fields[field] = getattr(self, field, None)
                
        return temporal_fields
    
    def has_standardized_concept(self, field_base: str) -> bool:
        """
        Check if a field has been mapped to a standard concept.
        
        Args:
            field_base: Base field name (e.g., 'drug' for 'drug_concept_id')
        
        Returns:
            True if the concept_id field exists and is not 0
        """
        concept_field = f"{field_base}_concept_id"
        if hasattr(self, concept_field):
            value = getattr(self, concept_field, None)
            return value is not None and value > 0
        return False
    
    @classmethod
    def model_validate_case_insensitive(cls, data: Dict[str, Any]) -> 'OmopModel':
        """
        Validate data with case-insensitive field matching.
        Useful for loading from CSV files with UPPER_SNAKE_CASE headers.
        
        Args:
            data: Dictionary with potentially case-mismatched keys
            
        Returns:
            Validated model instance
        """
        # Create a mapping of lowercase field names to actual field names
        field_map = {name.lower(): name for name in cls.model_fields}
        
        # Transform the input data to use correct field names
        normalized_data = {}
        for key, value in data.items():
            lower_key = key.lower()
            if lower_key in field_map:
                normalized_data[field_map[lower_key]] = value
            else:
                # Keep the original key if no match found (will be handled by validation)
                normalized_data[key] = value
        
        return cls.model_validate(normalized_data)
    
    def model_dump_upper(self, **kwargs) -> Dict[str, Any]:
        """
        Dump model to dictionary with UPPER_SNAKE_CASE field names.
        Useful for symmetric round-trip with case-insensitive loading.
        
        Args:
            **kwargs: Additional arguments passed to model_dump()
            
        Returns:
            Dictionary with UPPER_SNAKE_CASE keys
        """
        data = self.model_dump(**kwargs)
        return {key.upper(): value for key, value in data.items()}
    
    @classmethod
    def table_name(cls) -> str:
        """
        Get the OMOP CDM table name for this model class.
        
        Converts the class name to snake_case and handles special cases.
        This enables SQL/Arrow factory helpers and other table-level operations.
        
        Returns:
            The snake_case table name
        """
        name = cls.__name__
        
        # Handle special cases where class name doesn't match table name
        name_mappings = {
            'NoteExposure': 'note',
            'NoteNlp': 'note_nlp',
        }
        
        if name in name_mappings:
            return name_mappings[name]
        
        # Convert PascalCase to snake_case
        # Insert underscore before uppercase letters that follow lowercase letters
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
        
        return name.lower()
    
    @classmethod
    def get_primary_key_field(cls) -> Optional[str]:
        """
        Attempt to identify the primary key field.
        Usually it's the field that matches the table name + '_id'.
        """
        table_name = cls.table_name()
        pk_field = f"{table_name}_id"
        
        if pk_field in cls.model_fields:
            return pk_field
        
        return None
    
    def get_primary_key_value(self) -> Optional[int]:
        """
        Get the value of the primary key field.
        """
        pk_field = self.__class__.get_primary_key_field()
        if pk_field:
            return getattr(self, pk_field, None)
        return None
    
    @classmethod
    def primary_key_fields(cls) -> tuple[str, ...]:
        """
        Get the primary key field(s) for this model.
        Supports both single and composite primary keys.
        
        Returns:
            Tuple of field names that form the primary key
        """
        # First check if we have a defined primary key field
        if hasattr(cls, '_primary_key'):
            pk_attr = getattr(cls, '_primary_key')
            # Handle Pydantic ModelPrivateAttr
            if hasattr(pk_attr, 'default'):
                return (pk_attr.default,)
            elif isinstance(pk_attr, str):
                return (pk_attr,)
        
        # Try the standard pattern: table_name + '_id'
        pk_field = cls.get_primary_key_field()
        if pk_field:
            return (pk_field,)
        
        # For models with composite keys, check if fields are marked as primary key
        # This would need to be set during DDL parsing or manually
        pk_fields = []
        for field_name, field_info in cls.model_fields.items():
            # Guard against None json_schema_extra
            if field_info.json_schema_extra is not None and field_info.json_schema_extra.get('pk'):
                pk_fields.append(field_name)
        
        if pk_fields:
            return tuple(pk_fields)
        
        # Default: empty tuple if no primary key found
        return ()


class OmopClinicalModel(OmopModel):
    """
    Base model for OMOP clinical event tables.
    
    These tables contain patient-level clinical events and typically have:
    - person_id (required)
    - Date/datetime fields for when events occurred
    - Concept IDs for standardized clinical concepts
    - Type concept IDs for data provenance
    
    Includes additional validations specific to clinical data.
    """
    
    @model_validator(mode='after')
    def validate_person_id_exists(self) -> 'OmopClinicalModel':
        """
        Ensure clinical tables have a person_id field.
        """
        if not hasattr(self, 'person_id'):
            raise ValueError(f"{self.__class__.__name__} must have a person_id field")
        return self
    
    def get_person_id(self) -> int:
        """
        Get the person_id for this clinical record.
        """
        return getattr(self, 'person_id')


class OmopVocabularyModel(OmopModel):
    """
    Base model for OMOP vocabulary tables.
    
    These tables contain reference data for the standardized vocabularies and typically have:
    - valid_start_date and valid_end_date for temporal validity
    - No person_id field
    - Special validation rules for vocabulary data
    """
    
    @model_validator(mode='after')
    def validate_validity_dates(self) -> 'OmopVocabularyModel':
        """
        Validate vocabulary validity date ranges if they exist.
        """
        if hasattr(self, 'valid_start_date') and hasattr(self, 'valid_end_date'):
            start = getattr(self, 'valid_start_date', None)
            end = getattr(self, 'valid_end_date', None)
            
            if start and end and start > end:
                raise ValueError(
                    f"valid_start_date ({start}) must be before or equal to "
                    f"valid_end_date ({end})"
                )
        
        return self


class OmopReferenceModel(OmopModel):
    """
    Base model for OMOP reference/lookup tables.
    
    These tables contain configuration and reference data such as:
    - care_site, location, provider
    - cdm_source, metadata
    - cost, fact_relationship
    
    They don't follow the clinical event pattern but still benefit from
    base OMOP validations and utilities.
    """
    pass  # Inherits all functionality from OmopModel without additional constraints