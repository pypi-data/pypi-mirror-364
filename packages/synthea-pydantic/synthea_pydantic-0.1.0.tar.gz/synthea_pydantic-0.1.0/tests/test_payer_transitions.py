"""Tests for the payer_transitions module."""

import csv
from pathlib import Path
from uuid import UUID


from synthea_pydantic.payer_transitions import PayerTransition


def test_load_payer_transitions_csv():
    """Test loading payer transitions from CSV file."""
    csv_path = Path(__file__).parent / "data" / "csv" / "payer_transitions.csv"
    
    transitions = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            if i >= 100:  # Test first 100 rows for performance
                break
            transition = PayerTransition(**row)
            transitions.append(transition)
    
    # Verify we loaded some data
    assert len(transitions) > 0
    
    # Check the first transition
    first = transitions[0]
    assert first.patient == UUID('b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85')
    assert first.memberid == UUID('bca22051-b39b-7591-74d4-47e10a94c52e')
    assert first.start_year == 2019  # Extracted from "2019-02-24T05:07:38Z"
    assert first.end_year == 2020    # Extracted from "2020-03-01T05:07:38Z"
    assert first.payer == UUID('7c4411ce-02f1-39b5-b9ec-dfbea9ad3c1a')
    assert first.secondary_payer is None
    assert first.ownership == 'Self'
    assert first.owner_name == 'Damon455 Langosh790'


def test_payer_transition_serialization():
    """Test serializing PayerTransition models."""
    csv_path = Path(__file__).parent / "data" / "csv" / "payer_transitions.csv"
    
    transitions = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            if i >= 10:  # Test first 10 rows for performance
                break
            transition = PayerTransition(**row)
            transitions.append(transition)
    
    # Test model_dump() for all transitions
    for transition in transitions:
        data = transition.model_dump()
        assert isinstance(data, dict)
        assert 'patient' in data
        assert 'memberid' in data
        assert 'start_year' in data
        assert 'end_year' in data
        assert 'payer' in data
        assert 'secondary_payer' in data
        assert 'ownership' in data
        assert 'owner_name' in data
    
    # Test model_dump_json() for all transitions
    for transition in transitions:
        json_str = transition.model_dump_json()
        assert isinstance(json_str, str)
        assert '"patient"' in json_str
        assert '"start_year"' in json_str
        assert '"end_year"' in json_str
        assert '"payer"' in json_str
    
    # Test round-trip serialization
    first_transition = transitions[0]
    json_data = first_transition.model_dump_json()
    restored = PayerTransition.model_validate_json(json_data)
    assert restored == first_transition


def test_payer_transition_field_validation():
    """Test field validation for PayerTransition model."""
    # Test with all fields using lowercase names
    transition = PayerTransition(
        patient='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        memberid='bca22051-b39b-7591-74d4-47e10a94c52e',
        start_year=2019,
        end_year=2020,
        payer='7c4411ce-02f1-39b5-b9ec-dfbea9ad3c1a',
        secondary_payer='12345678-1234-1234-1234-123456789012',
        ownership='Self',
        owner_name='John Doe'
    )
    assert transition.patient == UUID('b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85')
    assert transition.memberid == UUID('bca22051-b39b-7591-74d4-47e10a94c52e')
    assert transition.start_year == 2019
    assert transition.end_year == 2020
    assert transition.payer == UUID('7c4411ce-02f1-39b5-b9ec-dfbea9ad3c1a')
    assert transition.secondary_payer == UUID('12345678-1234-1234-1234-123456789012')
    assert transition.ownership == 'Self'
    assert transition.owner_name == 'John Doe'
    
    # Test with minimal required fields (optional fields as None)
    transition_minimal = PayerTransition(
        patient='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        start_year=2019,
        end_year=2020,
        payer='7c4411ce-02f1-39b5-b9ec-dfbea9ad3c1a'
    )
    assert transition_minimal.memberid is None
    assert transition_minimal.secondary_payer is None
    assert transition_minimal.ownership is None
    assert transition_minimal.owner_name is None


def test_csv_direct_loading():
    """Test that CSV rows can be loaded directly with PayerTransition(**row)."""
    csv_path = Path(__file__).parent / "data" / "csv" / "payer_transitions.csv"
    
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        row = next(reader)
        
        # This should work directly now
        transition = PayerTransition(**row)
        
        # Verify it loaded correctly
        assert transition.patient == UUID('b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85')
        assert transition.memberid == UUID('bca22051-b39b-7591-74d4-47e10a94c52e')
        assert transition.start_year == 2019
        assert transition.end_year == 2020
        assert transition.payer == UUID('7c4411ce-02f1-39b5-b9ec-dfbea9ad3c1a')
        assert transition.ownership == 'Self'
        assert transition.owner_name == 'Damon455 Langosh790'


def test_ownership_validation():
    """Test that different ownership values are handled correctly."""
    csv_path = Path(__file__).parent / "data" / "csv" / "payer_transitions.csv"
    
    transitions = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            if i >= 200:  # Test first 200 rows to find variety
                break
            transition = PayerTransition(**row)
            transitions.append(transition)
    
    # Verify we have different ownership types
    ownership_types = {t.ownership for t in transitions if t.ownership is not None}
    
    # Should have multiple different ownership types
    assert len(ownership_types) > 0
    
    # Check some expected ownership types from the data
    expected_types = {'Guardian', 'Self', 'Spouse'}
    found_types = ownership_types.intersection(expected_types)
    assert len(found_types) > 0
    
    # Verify all ownership values are valid
    for transition in transitions:
        if transition.ownership is not None:
            assert transition.ownership in ['Guardian', 'Self', 'Spouse']


def test_year_extraction_from_datetime():
    """Test that years are correctly extracted from datetime strings."""
    # Test with datetime string format from CSV
    transition = PayerTransition(
        patient='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        start_year='2019-02-24T05:07:38Z',  # Should extract 2019
        end_year='2020-03-01T05:07:38Z',    # Should extract 2020
        payer='7c4411ce-02f1-39b5-b9ec-dfbea9ad3c1a'
    )
    assert transition.start_year == 2019
    assert transition.end_year == 2020
    
    # Test with different datetime formats
    transition2 = PayerTransition(
        patient='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        start_year='2021-12-31T23:59:59Z',  # Should extract 2021
        end_year='2022-01-01T00:00:00Z',    # Should extract 2022
        payer='7c4411ce-02f1-39b5-b9ec-dfbea9ad3c1a'
    )
    assert transition2.start_year == 2021
    assert transition2.end_year == 2022
    
    # Test with integer years (should pass through unchanged)
    transition3 = PayerTransition(
        patient='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        start_year=2023,  # Integer should work as-is
        end_year=2024,    # Integer should work as-is
        payer='7c4411ce-02f1-39b5-b9ec-dfbea9ad3c1a'
    )
    assert transition3.start_year == 2023
    assert transition3.end_year == 2024


def test_uuid_validation():
    """Test UUID field validation."""
    # Test with string UUIDs
    transition = PayerTransition(
        patient='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        memberid='bca22051-b39b-7591-74d4-47e10a94c52e',
        start_year=2019,
        end_year=2020,
        payer='7c4411ce-02f1-39b5-b9ec-dfbea9ad3c1a',
        secondary_payer='12345678-1234-1234-1234-123456789012'
    )
    assert isinstance(transition.patient, UUID)
    assert isinstance(transition.memberid, UUID)
    assert isinstance(transition.payer, UUID)
    assert isinstance(transition.secondary_payer, UUID)
    
    # Test with UUID objects
    patient_id = UUID('b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85')
    payer_id = UUID('7c4411ce-02f1-39b5-b9ec-dfbea9ad3c1a')
    transition_uuid_obj = PayerTransition(
        patient=patient_id,
        start_year=2019,
        end_year=2020,
        payer=payer_id
    )
    assert transition_uuid_obj.patient == patient_id
    assert transition_uuid_obj.payer == payer_id


def test_string_field_validation():
    """Test string field validation and whitespace handling."""
    # Test with extra whitespace
    transition = PayerTransition(
        patient='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        start_year=2019,
        end_year=2020,
        payer='7c4411ce-02f1-39b5-b9ec-dfbea9ad3c1a',
        ownership='  Self  ',  # Extra whitespace
        owner_name='  John Doe  '  # Extra whitespace
    )
    # Whitespace should be stripped due to str_strip_whitespace=True
    assert transition.ownership == 'Self'
    assert transition.owner_name == 'John Doe'


def test_empty_string_handling():
    """Test that empty strings in CSV are converted to None."""
    # Simulate a CSV row with empty strings
    csv_row = {
        'PATIENT': 'b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        'MEMBERID': 'bca22051-b39b-7591-74d4-47e10a94c52e',
        'START_YEAR': '2019-02-24T05:07:38Z',
        'END_YEAR': '2020-03-01T05:07:38Z',
        'PAYER': '7c4411ce-02f1-39b5-b9ec-dfbea9ad3c1a',
        'SECONDARY_PAYER': '',  # Empty string should become None
        'OWNERSHIP': 'Self',
        'OWNERNAME': 'John Doe'
    }
    
    transition = PayerTransition(**csv_row)
    
    assert transition.patient == UUID('b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85')
    assert transition.memberid == UUID('bca22051-b39b-7591-74d4-47e10a94c52e')
    assert transition.start_year == 2019
    assert transition.end_year == 2020
    assert transition.payer == UUID('7c4411ce-02f1-39b5-b9ec-dfbea9ad3c1a')
    assert transition.secondary_payer is None  # Empty string converted to None
    assert transition.ownership == 'Self'
    assert transition.owner_name == 'John Doe'


def test_year_range_validation():
    """Test that year ranges make sense."""
    csv_path = Path(__file__).parent / "data" / "csv" / "payer_transitions.csv"
    
    transitions = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            if i >= 50:  # Test first 50 rows
                break
            transition = PayerTransition(**row)
            transitions.append(transition)
    
    # Verify that start_year <= end_year for all transitions
    for transition in transitions:
        assert transition.start_year <= transition.end_year, \
            f"Start year {transition.start_year} should be <= end year {transition.end_year}"
    
    # Verify years are in reasonable range
    for transition in transitions:
        assert 1900 <= transition.start_year <= 2100, \
            f"Start year {transition.start_year} should be in reasonable range"
        assert 1900 <= transition.end_year <= 2100, \
            f"End year {transition.end_year} should be in reasonable range"


def test_payer_transition_model_config():
    """Test that the model configuration is working correctly."""
    # Test that str_strip_whitespace is working
    transition = PayerTransition(
        patient='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        start_year=2019,
        end_year=2020,
        payer='7c4411ce-02f1-39b5-b9ec-dfbea9ad3c1a',
        ownership='   Self   ',
        owner_name='   John Doe   '
    )
    
    assert transition.ownership == 'Self'
    assert transition.owner_name == 'John Doe'


def test_payer_transition_equality():
    """Test PayerTransition model equality comparison."""
    transition1 = PayerTransition(
        patient='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        memberid='bca22051-b39b-7591-74d4-47e10a94c52e',
        start_year=2019,
        end_year=2020,
        payer='7c4411ce-02f1-39b5-b9ec-dfbea9ad3c1a',
        ownership='Self',
        owner_name='John Doe'
    )
    
    transition2 = PayerTransition(
        patient='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        memberid='bca22051-b39b-7591-74d4-47e10a94c52e',
        start_year=2019,
        end_year=2020,
        payer='7c4411ce-02f1-39b5-b9ec-dfbea9ad3c1a',
        ownership='Self',
        owner_name='John Doe'
    )
    
    transition3 = PayerTransition(
        patient='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        memberid='bca22051-b39b-7591-74d4-47e10a94c52e',
        start_year=2019,
        end_year=2021,  # Different end year
        payer='7c4411ce-02f1-39b5-b9ec-dfbea9ad3c1a',
        ownership='Self',
        owner_name='John Doe'
    )
    
    assert transition1 == transition2
    assert transition1 != transition3


def test_guardian_ownership():
    """Test transitions with Guardian ownership."""
    csv_path = Path(__file__).parent / "data" / "csv" / "payer_transitions.csv"
    
    transitions = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            if i >= 100:  # Test first 100 rows to find Guardian ownership
                break
            transition = PayerTransition(**row)
            transitions.append(transition)
    
    # Find transitions with Guardian ownership
    guardian_transitions = [t for t in transitions if t.ownership == 'Guardian']
    
    # Should have some Guardian transitions in the data
    assert len(guardian_transitions) > 0
    
    # Verify Guardian transitions have owner names
    for transition in guardian_transitions:
        assert transition.owner_name is not None
        assert len(transition.owner_name.strip()) > 0


def test_multiple_transitions_same_patient():
    """Test that patients can have multiple payer transitions."""
    csv_path = Path(__file__).parent / "data" / "csv" / "payer_transitions.csv"
    
    transitions = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            if i >= 200:  # Test first 200 rows
                break
            transition = PayerTransition(**row)
            transitions.append(transition)
    
    # Group transitions by patient
    patient_transitions = {}
    for transition in transitions:
        patient_id = transition.patient
        if patient_id not in patient_transitions:
            patient_transitions[patient_id] = []
        patient_transitions[patient_id].append(transition)
    
    # Find patients with multiple transitions
    multi_transition_patients = {
        patient_id: transitions_list 
        for patient_id, transitions_list in patient_transitions.items() 
        if len(transitions_list) > 1
    }
    
    # Should have some patients with multiple transitions
    assert len(multi_transition_patients) > 0
    
    # Verify transitions for the same patient are chronologically ordered
    for patient_id, patient_trans in multi_transition_patients.items():
        # Sort by start year
        sorted_trans = sorted(patient_trans, key=lambda t: t.start_year)
        
        # Verify chronological order makes sense
        for i in range(len(sorted_trans) - 1):
            current = sorted_trans[i]
            next_trans = sorted_trans[i + 1]
            
            # Current transition should end before or when next one starts
            assert current.end_year <= next_trans.start_year, \
                f"Patient {patient_id}: transition ending {current.end_year} should be <= next starting {next_trans.start_year}" 