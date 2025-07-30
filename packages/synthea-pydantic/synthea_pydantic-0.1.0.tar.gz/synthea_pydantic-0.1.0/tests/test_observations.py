"""Tests for the observations module."""

import csv
from datetime import datetime
from pathlib import Path
from uuid import UUID


from synthea_pydantic.observations import Observation


def test_load_observations_csv():
    """Test loading observations from CSV file."""
    csv_path = Path(__file__).parent / "data" / "csv" / "observations.csv"
    
    observations = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            observation = Observation(**row)
            observations.append(observation)
    
    # Verify we loaded some data
    assert len(observations) > 0
    
    # Check the first observation
    first = observations[0]
    assert isinstance(first.date, datetime)
    assert isinstance(first.patient, UUID)
    assert first.encounter is None or isinstance(first.encounter, UUID)
    assert first.category is None or isinstance(first.category, str)
    assert isinstance(first.code, str)
    assert isinstance(first.description, str)
    assert first.value is None or isinstance(first.value, (str, float))
    assert first.units is None or isinstance(first.units, str)
    assert isinstance(first.type, str)


def test_observation_serialization():
    """Test serializing Observation models."""
    csv_path = Path(__file__).parent / "data" / "csv" / "observations.csv"
    
    observations = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            observation = Observation(**row)
            observations.append(observation)
    
    # Test model_dump() for all observations
    for observation in observations:
        data = observation.model_dump()
        assert isinstance(data, dict)
        assert 'date' in data
        assert 'patient' in data
        assert 'encounter' in data
        assert 'code' in data
        assert 'description' in data
        assert 'type' in data
    
    # Test model_dump_json() for all observations
    for observation in observations:
        json_str = observation.model_dump_json()
        assert isinstance(json_str, str)
        assert '"date"' in json_str
        assert '"patient"' in json_str
        assert '"encounter"' in json_str
        assert '"code"' in json_str
        assert '"description"' in json_str
        assert '"type"' in json_str
    
    # Test round-trip serialization
    first_observation = observations[0]
    json_data = first_observation.model_dump_json()
    restored = Observation.model_validate_json(json_data)
    assert restored == first_observation


def test_observation_field_validation():
    """Test field validation for Observation model."""
    # Test with numeric observation (e.g., blood pressure)
    observation_numeric = Observation(
        date='2020-01-01T10:00:00',
        patient='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        encounter='01efcc52-15d6-51e9-faa2-bee069fcbe44',
        category='vital-signs',
        code='55284-4',
        description='Blood pressure systolic',
        value=120.0,
        units='mmHg',
        type='numeric'
    )
    assert observation_numeric.date == datetime(2020, 1, 1, 10, 0, 0)
    assert observation_numeric.value == 120.0
    assert observation_numeric.units == 'mmHg'
    assert observation_numeric.type == 'numeric'
    
    # Test with text observation (e.g., survey response)
    observation_text = Observation(
        date='2020-01-01T11:00:00',
        patient='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        encounter='01efcc52-15d6-51e9-faa2-bee069fcbe44',
        category='survey',
        code='75626-2',
        description='Total score [DAST-10]',
        value='Never',
        units=None,
        type='text'
    )
    assert observation_text.value == 'Never'
    assert observation_text.units is None
    assert observation_text.type == 'text'
    
    # Test with minimal required fields
    observation_minimal = Observation(
        date='2020-01-01T12:00:00',
        patient='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        encounter='01efcc52-15d6-51e9-faa2-bee069fcbe44',
        code='8302-2',
        description='Body Height',
        type='numeric'
    )
    assert observation_minimal.category is None
    assert observation_minimal.value is None
    assert observation_minimal.units is None


def test_csv_direct_loading():
    """Test that CSV rows can be loaded directly with Observation(**row)."""
    csv_path = Path(__file__).parent / "data" / "csv" / "observations.csv"
    
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        row = next(reader)
        
        # This should work directly now
        observation = Observation(**row)
        
        # Verify it loaded correctly
        assert isinstance(observation.date, datetime)
        assert isinstance(observation.patient, UUID)
        assert observation.encounter is None or isinstance(observation.encounter, UUID)
        assert isinstance(observation.code, str)
        assert isinstance(observation.description, str)
        assert isinstance(observation.type, str)


def test_empty_string_handling():
    """Test that empty strings in CSV are converted to None."""
    # Simulate a CSV row with empty strings
    csv_row = {
        'DATE': '2020-01-01T10:00:00',
        'PATIENT': 'b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        'ENCOUNTER': '01efcc52-15d6-51e9-faa2-bee069fcbe44',
        'CATEGORY': '',  # Empty string should become None
        'CODE': '8302-2',
        'DESCRIPTION': 'Body Height',
        'VALUE': '',  # Empty string should become None
        'UNITS': '',  # Empty string should become None
        'TYPE': 'numeric'
    }
    
    observation = Observation(**csv_row)
    
    assert observation.category is None
    assert observation.value is None
    assert observation.units is None


def test_numeric_value_conversion():
    """Test that numeric values are properly converted when TYPE is numeric."""
    # Test with numeric type and numeric value string
    csv_row_numeric = {
        'DATE': '2020-01-01T10:00:00',
        'PATIENT': 'b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        'ENCOUNTER': '01efcc52-15d6-51e9-faa2-bee069fcbe44',
        'CATEGORY': 'vital-signs',
        'CODE': '29463-7',
        'DESCRIPTION': 'Body Weight',
        'VALUE': '75.5',  # String that should be converted to float
        'UNITS': 'kg',
        'TYPE': 'numeric'
    }
    
    observation = Observation(**csv_row_numeric)
    assert observation.value == 75.5
    assert isinstance(observation.value, float)
    
    # Test with text type value stays as string
    csv_row_text = {
        'DATE': '2020-01-01T10:00:00',
        'PATIENT': 'b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        'ENCOUNTER': '01efcc52-15d6-51e9-faa2-bee069fcbe44',
        'CATEGORY': 'survey',
        'CODE': '75626-2',
        'DESCRIPTION': 'Total score [DAST-10]',
        'VALUE': 'Never',
        'UNITS': '',
        'TYPE': 'text'
    }
    
    observation_text = Observation(**csv_row_text)
    assert observation_text.value == 'Never'
    assert isinstance(observation_text.value, str)