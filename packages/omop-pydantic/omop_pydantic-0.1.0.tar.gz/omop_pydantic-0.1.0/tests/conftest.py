"""
Shared pytest configuration and fixtures for omop-pydantic tests.
"""
import csv
import pytest
from pathlib import Path
from typing import Dict, List, Any


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")  
def omop_csv_dir(test_data_dir) -> Path:
    """Path to OMOP CSV files."""
    return test_data_dir / "omop"


@pytest.fixture
def sample_person_data() -> Dict[str, Any]:
    """Sample person data for testing."""
    return {
        "person_id": 1,
        "gender_concept_id": 8532,  # Female
        "year_of_birth": 1990,
        "month_of_birth": 6,
        "day_of_birth": 15,
        "race_concept_id": 8527,    # White
        "ethnicity_concept_id": 0,  # No matching concept
    }


@pytest.fixture
def sample_concept_data() -> Dict[str, Any]:
    """Sample concept data for testing."""
    return {
        "concept_id": 8532,
        "concept_name": "FEMALE",
        "domain_id": "Gender",
        "vocabulary_id": "Gender",
        "concept_class_id": "Gender",
        "standard_concept": "S",
        "concept_code": "F",
        "valid_start_date": "1970-01-01",
        "valid_end_date": "2099-12-31",
        "invalid_reason": None,
    }


def load_csv_sample(csv_path: Path, limit: int = 5) -> List[Dict[str, Any]]:
    """Load first N rows from CSV file."""
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if limit is not None and i >= limit:
                break
            # Convert empty strings to None for optional fields
            cleaned_row = {k: (v if v != '' else None) for k, v in row.items()}
            rows.append(cleaned_row)
    return rows


@pytest.fixture
def csv_loader():
    """Fixture that provides the CSV loading utility."""
    return load_csv_sample