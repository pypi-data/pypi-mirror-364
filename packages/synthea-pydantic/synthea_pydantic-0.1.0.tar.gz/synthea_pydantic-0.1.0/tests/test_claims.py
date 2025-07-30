"""Tests for the claims module."""

import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID


from synthea_pydantic.claims import Claim


def test_load_claims_csv():
    """Test loading claims from CSV file."""
    csv_path = Path(__file__).parent / "data" / "csv" / "claims.csv"
    
    claims = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            claim = Claim(**row)
            claims.append(claim)
    
    # Verify we loaded some data
    assert len(claims) > 0
    
    # Check the first claim
    first = claims[0]
    assert isinstance(first.id, UUID)
    assert isinstance(first.patientid, UUID)
    assert isinstance(first.providerid, UUID)
    assert first.primarypatientinsuranceid is None or isinstance(first.primarypatientinsuranceid, UUID)
    assert first.secondarypatientinsuranceid is None or isinstance(first.secondarypatientinsuranceid, UUID)
    assert isinstance(first.departmentid, int)
    assert isinstance(first.patientdepartmentid, int)
    assert first.diagnosis1 is None or isinstance(first.diagnosis1, str)
    assert first.diagnosis2 is None or isinstance(first.diagnosis2, str)
    assert first.diagnosis3 is None or isinstance(first.diagnosis3, str)
    assert first.diagnosis4 is None or isinstance(first.diagnosis4, str)
    assert first.diagnosis5 is None or isinstance(first.diagnosis5, str)
    assert first.diagnosis6 is None or isinstance(first.diagnosis6, str)
    assert first.diagnosis7 is None or isinstance(first.diagnosis7, str)
    assert first.diagnosis8 is None or isinstance(first.diagnosis8, str)
    assert first.referringproviderid is None or isinstance(first.referringproviderid, UUID)
    assert first.appointmentid is None or isinstance(first.appointmentid, UUID)
    assert isinstance(first.currentillnessdate, datetime)
    assert isinstance(first.servicedate, datetime)
    assert first.supervisingproviderid is None or isinstance(first.supervisingproviderid, UUID)
    assert first.status1 is None or first.status1 in ["BILLED", "CLOSED"]
    assert first.status2 is None or first.status2 in ["BILLED", "CLOSED"]
    assert first.statusp is None or first.statusp in ["BILLED", "CLOSED"]
    assert first.outstanding1 is None or isinstance(first.outstanding1, Decimal)
    assert first.outstanding2 is None or isinstance(first.outstanding2, Decimal)
    assert first.outstandingp is None or isinstance(first.outstandingp, Decimal)
    assert first.lastbilleddate1 is None or isinstance(first.lastbilleddate1, datetime)
    assert first.lastbilleddate2 is None or isinstance(first.lastbilleddate2, datetime)
    assert first.lastbilleddatep is None or isinstance(first.lastbilleddatep, datetime)
    assert first.healthcareclaimtypeid1 is None or first.healthcareclaimtypeid1 in [1, 2]
    assert first.healthcareclaimtypeid2 is None or first.healthcareclaimtypeid2 in [1, 2]


def test_claim_serialization():
    """Test serializing Claim models."""
    csv_path = Path(__file__).parent / "data" / "csv" / "claims.csv"
    
    claims = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            claim = Claim(**row)
            claims.append(claim)
    
    # Test model_dump() for all claims
    for claim in claims:
        data = claim.model_dump()
        assert isinstance(data, dict)
        assert 'id' in data
        assert 'patientid' in data
        assert 'providerid' in data
        assert 'departmentid' in data
        assert 'patientdepartmentid' in data
        assert 'currentillnessdate' in data
        assert 'servicedate' in data
    
    # Test model_dump_json() for all claims
    for claim in claims:
        json_str = claim.model_dump_json()
        assert isinstance(json_str, str)
        assert '"id"' in json_str
        assert '"patientid"' in json_str
        assert '"providerid"' in json_str
        assert '"currentillnessdate"' in json_str
        assert '"servicedate"' in json_str
    
    # Test round-trip serialization
    first_claim = claims[0]
    json_data = first_claim.model_dump_json()
    restored = Claim.model_validate_json(json_data)
    assert restored == first_claim


def test_claim_field_validation():
    """Test field validation for Claim model."""
    # Test with minimal required fields using lowercase names
    claim = Claim(
        id='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        patientid='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        providerid='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        departmentid=1,
        patientdepartmentid=1,
        currentillnessdate='2020-01-01T00:00:00',
        servicedate='2020-01-01T00:00:00'
    )
    assert claim.currentillnessdate == datetime(2020, 1, 1, 0, 0, 0)
    assert claim.servicedate == datetime(2020, 1, 1, 0, 0, 0)
    assert claim.primarypatientinsuranceid is None
    assert claim.secondarypatientinsuranceid is None
    assert claim.diagnosis1 is None
    assert claim.referringproviderid is None
    assert claim.appointmentid is None
    assert claim.supervisingproviderid is None
    assert claim.status1 is None
    assert claim.status2 is None
    assert claim.statusp is None
    assert claim.outstanding1 is None
    assert claim.outstanding2 is None
    assert claim.outstandingp is None
    assert claim.lastbilleddate1 is None
    assert claim.lastbilleddate2 is None
    assert claim.lastbilleddatep is None
    assert claim.healthcareclaimtypeid1 is None
    assert claim.healthcareclaimtypeid2 is None
    
    # Test with all fields
    claim_full = Claim(
        id='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        patientid='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        providerid='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        primarypatientinsuranceid='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        secondarypatientinsuranceid='01efcc52-15d6-51e9-faa2-bee069fcbe44',
        departmentid=1,
        patientdepartmentid=2,
        diagnosis1='123456',
        diagnosis2='234567',
        diagnosis3='345678',
        diagnosis4='456789',
        diagnosis5='567890',
        diagnosis6='678901',
        diagnosis7='789012',
        diagnosis8='890123',
        referringproviderid='01efcc52-15d6-51e9-faa2-bee069fcbe44',
        appointmentid='01efcc52-15d6-51e9-faa2-bee069fcbe44',
        currentillnessdate='2020-01-01T00:00:00',
        servicedate='2020-01-01T00:00:00',
        supervisingproviderid='01efcc52-15d6-51e9-faa2-bee069fcbe44',
        status1='BILLED',
        status2='CLOSED',
        statusp='BILLED',
        outstanding1='100.50',
        outstanding2='200.75',
        outstandingp='50.25',
        lastbilleddate1='2020-01-02T00:00:00',
        lastbilleddate2='2020-01-03T00:00:00',
        lastbilleddatep='2020-01-04T00:00:00',
        healthcareclaimtypeid1=1,
        healthcareclaimtypeid2=2
    )
    assert claim_full.primarypatientinsuranceid == UUID('b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85')
    assert claim_full.diagnosis1 == '123456'
    assert claim_full.diagnosis8 == '890123'
    assert claim_full.status1 == 'BILLED'
    assert claim_full.status2 == 'CLOSED'
    assert claim_full.statusp == 'BILLED'
    assert claim_full.outstanding1 == Decimal('100.50')
    assert claim_full.outstanding2 == Decimal('200.75')
    assert claim_full.outstandingp == Decimal('50.25')
    assert claim_full.lastbilleddate1 == datetime(2020, 1, 2, 0, 0, 0)
    assert claim_full.healthcareclaimtypeid1 == 1
    assert claim_full.healthcareclaimtypeid2 == 2


def test_csv_direct_loading():
    """Test that CSV rows can be loaded directly with Claim(**row)."""
    csv_path = Path(__file__).parent / "data" / "csv" / "claims.csv"
    
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        row = next(reader)
        
        # This should work directly now
        claim = Claim(**row)
        
        # Verify it loaded correctly
        assert isinstance(claim.id, UUID)
        assert isinstance(claim.patientid, UUID)
        assert isinstance(claim.providerid, UUID)
        assert isinstance(claim.departmentid, int)
        assert isinstance(claim.patientdepartmentid, int)
        assert isinstance(claim.currentillnessdate, datetime)
        assert isinstance(claim.servicedate, datetime)


def test_empty_string_handling():
    """Test that empty strings in CSV are converted to None."""
    # Simulate a CSV row with empty strings
    csv_row = {
        'Id': 'b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        'PATIENTID': 'b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        'PROVIDERID': 'b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        'PRIMARYPATIENTINSURANCEID': '',  # Empty string should become None
        'SECONDARYPATIENTINSURANCEID': '',  # Empty string should become None
        'DEPARTMENTID': '1',
        'PATIENTDEPARTMENTID': '1',
        'DIAGNOSIS1': '',  # Empty string should become None
        'DIAGNOSIS2': '',  # Empty string should become None
        'DIAGNOSIS3': '',  # Empty string should become None
        'DIAGNOSIS4': '',  # Empty string should become None
        'DIAGNOSIS5': '',  # Empty string should become None
        'DIAGNOSIS6': '',  # Empty string should become None
        'DIAGNOSIS7': '',  # Empty string should become None
        'DIAGNOSIS8': '',  # Empty string should become None
        'REFERRINGPROVIDERID': '',  # Empty string should become None
        'APPOINTMENTID': '',  # Empty string should become None
        'CURRENTILLNESSDATE': '2020-01-01T00:00:00',
        'SERVICEDATE': '2020-01-01T00:00:00',
        'SUPERVISINGPROVIDERID': '',  # Empty string should become None
        'STATUS1': '',  # Empty string should become None
        'STATUS2': '',  # Empty string should become None
        'STATUSP': '',  # Empty string should become None
        'OUTSTANDING1': '',  # Empty string should become None
        'OUTSTANDING2': '',  # Empty string should become None
        'OUTSTANDINGP': '',  # Empty string should become None
        'LASTBILLEDDATE1': '',  # Empty string should become None
        'LASTBILLEDDATE2': '',  # Empty string should become None
        'LASTBILLEDDATEP': '',  # Empty string should become None
        'HEALTHCARECLAIMTYPEID1': '',  # Empty string should become None
        'HEALTHCARECLAIMTYPEID2': '',  # Empty string should become None
    }
    
    claim = Claim(**csv_row)
    
    assert claim.primarypatientinsuranceid is None
    assert claim.secondarypatientinsuranceid is None
    assert claim.diagnosis1 is None
    assert claim.diagnosis2 is None
    assert claim.diagnosis3 is None
    assert claim.diagnosis4 is None
    assert claim.diagnosis5 is None
    assert claim.diagnosis6 is None
    assert claim.diagnosis7 is None
    assert claim.diagnosis8 is None
    assert claim.referringproviderid is None
    assert claim.appointmentid is None
    assert claim.supervisingproviderid is None
    assert claim.status1 is None
    assert claim.status2 is None
    assert claim.statusp is None
    assert claim.outstanding1 is None
    assert claim.outstanding2 is None
    assert claim.outstandingp is None
    assert claim.lastbilleddate1 is None
    assert claim.lastbilleddate2 is None
    assert claim.lastbilleddatep is None
    assert claim.healthcareclaimtypeid1 is None
    assert claim.healthcareclaimtypeid2 is None