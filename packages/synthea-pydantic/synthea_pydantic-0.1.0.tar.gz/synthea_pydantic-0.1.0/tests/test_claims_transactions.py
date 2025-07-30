"""Tests for the claims_transactions module."""

import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID


from synthea_pydantic.claims_transactions import ClaimTransaction


def test_load_claims_transactions_csv():
    """Test loading claims transactions from CSV file."""
    csv_path = Path(__file__).parent / "data" / "csv" / "claims_transactions.csv"
    
    transactions = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            transaction = ClaimTransaction(**row)
            transactions.append(transaction)
    
    # Verify we loaded some data
    assert len(transactions) > 0
    
    # Check the first transaction
    first = transactions[0]
    assert isinstance(first.id, UUID)
    assert isinstance(first.claimid, UUID)
    assert isinstance(first.chargeid, int)
    assert isinstance(first.patientid, UUID)
    assert first.type in ["CHARGE", "PAYMENT", "ADJUSTMENT", "TRANSFERIN", "TRANSFEROUT"]
    assert first.amount is None or isinstance(first.amount, Decimal)
    assert first.method is None or first.method in ["CASH", "CHECK", "ECHECK", "COPAY", "SYSTEM", "CC"]
    assert first.fromdate is None or isinstance(first.fromdate, datetime)
    assert first.todate is None or isinstance(first.todate, datetime)
    assert isinstance(first.placeofservice, UUID)
    assert isinstance(first.procedurecode, str)
    assert first.modifier1 is None or isinstance(first.modifier1, str)
    assert first.modifier2 is None or isinstance(first.modifier2, str)
    assert first.diagnosisref1 is None or first.diagnosisref1 in [1, 2, 3, 4, 5, 6, 7, 8]
    assert first.diagnosisref2 is None or first.diagnosisref2 in [1, 2, 3, 4, 5, 6, 7, 8]
    assert first.diagnosisref3 is None or first.diagnosisref3 in [1, 2, 3, 4, 5, 6, 7, 8]
    assert first.diagnosisref4 is None or first.diagnosisref4 in [1, 2, 3, 4, 5, 6, 7, 8]
    assert first.units is None or isinstance(first.units, int)
    assert first.departmentid is None or isinstance(first.departmentid, int)
    assert first.notes is None or isinstance(first.notes, str)
    assert first.unitamount is None or isinstance(first.unitamount, Decimal)
    assert first.transferoutid is None or isinstance(first.transferoutid, int)
    assert first.transfertype is None or first.transfertype in ["1", "2", "p"]
    assert first.payments is None or isinstance(first.payments, Decimal)
    assert first.adjustments is None or isinstance(first.adjustments, Decimal)
    assert first.transfers is None or isinstance(first.transfers, Decimal)
    assert first.outstanding is None or isinstance(first.outstanding, Decimal)
    assert first.appointmentid is None or isinstance(first.appointmentid, UUID)
    assert first.linenote is None or isinstance(first.linenote, str)
    assert first.patientinsuranceid is None or isinstance(first.patientinsuranceid, UUID)
    assert first.feescheduleid is None or isinstance(first.feescheduleid, int)
    assert isinstance(first.providerid, UUID)
    assert first.supervisingproviderid is None or isinstance(first.supervisingproviderid, UUID)


def test_claim_transaction_serialization():
    """Test serializing ClaimTransaction models."""
    csv_path = Path(__file__).parent / "data" / "csv" / "claims_transactions.csv"
    
    transactions = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            transaction = ClaimTransaction(**row)
            transactions.append(transaction)
    
    # Test model_dump() for all transactions
    for transaction in transactions:
        data = transaction.model_dump()
        assert isinstance(data, dict)
        assert 'id' in data
        assert 'claimid' in data
        assert 'chargeid' in data
        assert 'patientid' in data
        assert 'type' in data
        assert 'placeofservice' in data
        assert 'procedurecode' in data
        assert 'providerid' in data
    
    # Test model_dump_json() for all transactions
    for transaction in transactions:
        json_str = transaction.model_dump_json()
        assert isinstance(json_str, str)
        assert '"id"' in json_str
        assert '"claimid"' in json_str
        assert '"chargeid"' in json_str
        assert '"patientid"' in json_str
        assert '"type"' in json_str
        assert '"procedurecode"' in json_str
    
    # Test round-trip serialization
    first_transaction = transactions[0]
    json_data = first_transaction.model_dump_json()
    restored = ClaimTransaction.model_validate_json(json_data)
    assert restored == first_transaction


def test_claim_transaction_field_validation():
    """Test field validation for ClaimTransaction model."""
    # Test with minimal required fields using lowercase names
    transaction = ClaimTransaction(
        id='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        claimid='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        chargeid=1,
        patientid='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        type='CHARGE',
        placeofservice='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        procedurecode='123456',
        providerid='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85'
    )
    assert transaction.type == 'CHARGE'
    assert transaction.amount is None
    assert transaction.method is None
    assert transaction.fromdate is None
    assert transaction.todate is None
    assert transaction.modifier1 is None
    assert transaction.modifier2 is None
    assert transaction.diagnosisref1 is None
    assert transaction.units is None
    assert transaction.departmentid is None
    assert transaction.notes is None
    assert transaction.unitamount is None
    assert transaction.transferoutid is None
    assert transaction.transfertype is None
    assert transaction.payments is None
    assert transaction.adjustments is None
    assert transaction.transfers is None
    assert transaction.outstanding is None
    assert transaction.appointmentid is None
    assert transaction.linenote is None
    assert transaction.patientinsuranceid is None
    assert transaction.feescheduleid is None
    assert transaction.supervisingproviderid is None
    
    # Test with all fields
    transaction_full = ClaimTransaction(
        id='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        claimid='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        chargeid=1,
        patientid='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        type='PAYMENT',
        amount='100.50',
        method='CHECK',
        fromdate='2020-01-01T00:00:00',
        todate='2020-01-02T00:00:00',
        placeofservice='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        procedurecode='123456',
        modifier1='A1',
        modifier2='B2',
        diagnosisref1=1,
        diagnosisref2=2,
        diagnosisref3=3,
        diagnosisref4=4,
        units=2,
        departmentid=10,
        notes='Test transaction',
        unitamount='50.25',
        transferoutid=999,
        transfertype='1',
        payments='100.50',
        adjustments='0.00',
        transfers='0.00',
        outstanding='0.00',
        appointmentid='01efcc52-15d6-51e9-faa2-bee069fcbe44',
        linenote='Payment received',
        patientinsuranceid='01efcc52-15d6-51e9-faa2-bee069fcbe44',
        feescheduleid=1,
        providerid='b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        supervisingproviderid='01efcc52-15d6-51e9-faa2-bee069fcbe44'
    )
    assert transaction_full.type == 'PAYMENT'
    assert transaction_full.amount == Decimal('100.50')
    assert transaction_full.method == 'CHECK'
    assert transaction_full.fromdate == datetime(2020, 1, 1, 0, 0, 0)
    assert transaction_full.todate == datetime(2020, 1, 2, 0, 0, 0)
    assert transaction_full.modifier1 == 'A1'
    assert transaction_full.modifier2 == 'B2'
    assert transaction_full.diagnosisref1 == 1
    assert transaction_full.diagnosisref2 == 2
    assert transaction_full.diagnosisref3 == 3
    assert transaction_full.diagnosisref4 == 4
    assert transaction_full.units == 2
    assert transaction_full.departmentid == 10
    assert transaction_full.notes == 'Test transaction'
    assert transaction_full.unitamount == Decimal('50.25')
    assert transaction_full.transferoutid == 999
    assert transaction_full.transfertype == '1'
    assert transaction_full.payments == Decimal('100.50')
    assert transaction_full.adjustments == Decimal('0.00')
    assert transaction_full.transfers == Decimal('0.00')
    assert transaction_full.outstanding == Decimal('0.00')
    assert transaction_full.appointmentid == UUID('01efcc52-15d6-51e9-faa2-bee069fcbe44')
    assert transaction_full.linenote == 'Payment received'
    assert transaction_full.patientinsuranceid == UUID('01efcc52-15d6-51e9-faa2-bee069fcbe44')
    assert transaction_full.feescheduleid == 1
    assert transaction_full.supervisingproviderid == UUID('01efcc52-15d6-51e9-faa2-bee069fcbe44')


def test_csv_direct_loading():
    """Test that CSV rows can be loaded directly with ClaimTransaction(**row)."""
    csv_path = Path(__file__).parent / "data" / "csv" / "claims_transactions.csv"
    
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        row = next(reader)
        
        # This should work directly now
        transaction = ClaimTransaction(**row)
        
        # Verify it loaded correctly
        assert isinstance(transaction.id, UUID)
        assert isinstance(transaction.claimid, UUID)
        assert isinstance(transaction.chargeid, int)
        assert isinstance(transaction.patientid, UUID)
        assert transaction.type in ["CHARGE", "PAYMENT", "ADJUSTMENT", "TRANSFERIN", "TRANSFEROUT"]
        assert isinstance(transaction.placeofservice, UUID)
        assert isinstance(transaction.procedurecode, str)
        assert isinstance(transaction.providerid, UUID)


def test_empty_string_handling():
    """Test that empty strings in CSV are converted to None."""
    # Simulate a CSV row with empty strings
    csv_row = {
        'ID': 'b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        'CLAIMID': 'b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        'CHARGEID': '1',
        'PATIENTID': 'b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        'TYPE': 'CHARGE',
        'AMOUNT': '',  # Empty string should become None
        'METHOD': '',  # Empty string should become None
        'FROMDATE': '',  # Empty string should become None
        'TODATE': '',  # Empty string should become None
        'PLACEOFSERVICE': 'b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        'PROCEDURECODE': '123456',
        'MODIFIER1': '',  # Empty string should become None
        'MODIFIER2': '',  # Empty string should become None
        'DIAGNOSISREF1': '',  # Empty string should become None
        'DIAGNOSISREF2': '',  # Empty string should become None
        'DIAGNOSISREF3': '',  # Empty string should become None
        'DIAGNOSISREF4': '',  # Empty string should become None
        'UNITS': '',  # Empty string should become None
        'DEPARTMENTID': '',  # Empty string should become None
        'NOTES': '',  # Empty string should become None
        'UNITAMOUNT': '',  # Empty string should become None
        'TRANSFEROUTID': '',  # Empty string should become None
        'TRANSFERTYPE': '',  # Empty string should become None
        'PAYMENTS': '',  # Empty string should become None
        'ADJUSTMENTS': '',  # Empty string should become None
        'TRANSFERS': '',  # Empty string should become None
        'OUTSTANDING': '',  # Empty string should become None
        'APPOINTMENTID': '',  # Empty string should become None
        'LINENOTE': '',  # Empty string should become None
        'PATIENTINSURANCEID': '',  # Empty string should become None
        'FEESCHEDULEID': '',  # Empty string should become None
        'PROVIDERID': 'b9c610cd-28a6-4636-ccb6-c7a0d2a4cb85',
        'SUPERVISINGPROVIDERID': '',  # Empty string should become None
    }
    
    transaction = ClaimTransaction(**csv_row)
    
    assert transaction.amount is None
    assert transaction.method is None
    assert transaction.fromdate is None
    assert transaction.todate is None
    assert transaction.modifier1 is None
    assert transaction.modifier2 is None
    assert transaction.diagnosisref1 is None
    assert transaction.diagnosisref2 is None
    assert transaction.diagnosisref3 is None
    assert transaction.diagnosisref4 is None
    assert transaction.units is None
    assert transaction.departmentid is None
    assert transaction.notes is None
    assert transaction.unitamount is None
    assert transaction.transferoutid is None
    assert transaction.transfertype is None
    assert transaction.payments is None
    assert transaction.adjustments is None
    assert transaction.transfers is None
    assert transaction.outstanding is None
    assert transaction.appointmentid is None
    assert transaction.linenote is None
    assert transaction.patientinsuranceid is None
    assert transaction.feescheduleid is None
    assert transaction.supervisingproviderid is None