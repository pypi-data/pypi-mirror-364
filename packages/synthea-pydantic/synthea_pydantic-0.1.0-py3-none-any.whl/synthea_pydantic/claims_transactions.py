"""Pydantic models for Synthea claims_transactions CSV format."""

from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional
from uuid import UUID

from pydantic import Field, model_validator

from .base import SyntheaBaseModel


class ClaimTransaction(SyntheaBaseModel):
    """Model representing a single claim transaction record from Synthea CSV output."""
    
    id: UUID = Field(alias='ID', description="Primary Key. Unique Identifier of the claim transaction")
    claimid: UUID = Field(alias='CLAIMID', description="Foreign key to the Claim")
    chargeid: int = Field(alias='CHARGEID', description="Charge ID")
    patientid: UUID = Field(alias='PATIENTID', description="Foreign key to the Patient")
    type: Literal["CHARGE", "PAYMENT", "ADJUSTMENT", "TRANSFERIN", "TRANSFEROUT"] = Field(
        alias='TYPE',
        description="CHARGE: original line item. PAYMENT: payment made against a charge by an insurance company (aka Payer) or patient. ADJUSTMENT: change in the charge without a payment, made by an insurance company. TRANSFERIN and TRANSFEROUT: transfer of the balance from one insurance company to another, or to a patient"
    )
    amount: Optional[Decimal] = Field(None, alias='AMOUNT', description="Dollar amount for a CHARGE or TRANSFERIN")
    method: Optional[Literal["CASH", "CHECK", "ECHECK", "COPAY", "SYSTEM", "CC"]] = Field(
        None, alias='METHOD', description="Payment made by CASH, CHECK, ECHECK, COPAY, SYSTEM (adjustments without payment), or CC (credit card)"
    )
    fromdate: Optional[datetime] = Field(None, alias='FROMDATE', description="Transaction start date")
    todate: Optional[datetime] = Field(None, alias='TODATE', description="Transaction end date")
    placeofservice: UUID = Field(alias='PLACEOFSERVICE', description="Foreign key to the Organization")
    procedurecode: str = Field(alias='PROCEDURECODE', description="SNOMED-CT or other code (e.g. CVX for Vaccines) for the service")
    modifier1: Optional[str] = Field(None, alias='MODIFIER1', description="Unused. Modifier on procedure code")
    modifier2: Optional[str] = Field(None, alias='MODIFIER2', description="Unused. Modifier on procedure code")
    diagnosisref1: Optional[Literal[1, 2, 3, 4, 5, 6, 7, 8]] = Field(
        None, alias='DIAGNOSISREF1', description="Number indicating which diagnosis code from the claim applies to this transaction, 1-8 are valid options"
    )
    diagnosisref2: Optional[Literal[1, 2, 3, 4, 5, 6, 7, 8]] = Field(
        None, alias='DIAGNOSISREF2', description="Number indicating which diagnosis code from the claim applies to this transaction, 1-8 are valid options"
    )
    diagnosisref3: Optional[Literal[1, 2, 3, 4, 5, 6, 7, 8]] = Field(
        None, alias='DIAGNOSISREF3', description="Number indicating which diagnosis code from the claim applies to this transaction, 1-8 are valid options"
    )
    diagnosisref4: Optional[Literal[1, 2, 3, 4, 5, 6, 7, 8]] = Field(
        None, alias='DIAGNOSISREF4', description="Number indicating which diagnosis code from the claim applies to this transaction, 1-8 are valid options"
    )
    units: Optional[int] = Field(None, alias='UNITS', description="Number of units of the service")
    departmentid: Optional[int] = Field(None, alias='DEPARTMENTID', description="Placeholder for department")
    notes: Optional[str] = Field(None, alias='NOTES', description="Description of the service or transaction")
    unitamount: Optional[Decimal] = Field(None, alias='UNITAMOUNT', description="Cost per unit")
    transferoutid: Optional[int] = Field(None, alias='TRANSFEROUTID', description="If the transaction is a TRANSFERIN, the Charge ID of the corresponding TRANSFEROUT row")
    transfertype: Optional[Literal["1", "2", "p"]] = Field(
        None, alias='TRANSFERTYPE', description="1 if transferred to the primary insurance, 2 if transferred to the secondary insurance, or p if transferred to the patient"
    )
    payments: Optional[Decimal] = Field(None, alias='PAYMENTS', description="Dollar amount of a payment for a PAYMENT row")
    adjustments: Optional[Decimal] = Field(None, alias='ADJUSTMENTS', description="Dollar amount of an adjustment for an ADJUSTMENTS row")
    transfers: Optional[Decimal] = Field(None, alias='TRANSFERS', description="Dollar amount of a transfer for a TRANSFERIN or TRANSFEROUT row")
    outstanding: Optional[Decimal] = Field(None, alias='OUTSTANDING', description="Dollar amount left unpaid after this transaction was applied")
    appointmentid: Optional[UUID] = Field(None, alias='APPOINTMENTID', description="Foreign key to the Encounter")
    linenote: Optional[str] = Field(None, alias='LINENOTE', description="Note")
    patientinsuranceid: Optional[UUID] = Field(None, alias='PATIENTINSURANCEID', description="Foreign key to the Payer Transitions table member ID")
    feescheduleid: Optional[int] = Field(None, alias='FEESCHEDULEID', description="Fixed to 1")
    providerid: UUID = Field(alias='PROVIDERID', description="Foreign key to the Provider")
    supervisingproviderid: Optional[UUID] = Field(None, alias='SUPERVISINGPROVIDERID', description="Foreign key to the supervising Provider")
    
    @model_validator(mode='before')
    @classmethod
    def preprocess_csv(cls, data):
        """Convert empty strings to None and handle special values."""
        # First apply the base preprocessing
        data = super().preprocess_csv(data)
        
        if isinstance(data, dict):
            processed = data.copy()
            for k, v in data.items():
                # Handle '0' as None for UUID fields that use '0' as a null value
                if k in ['PATIENTINSURANCEID'] and v == '0':
                    processed[k] = None
                # Convert string numbers to integers for diagnosis refs
                elif k in ['DIAGNOSISREF1', 'DIAGNOSISREF2', 'DIAGNOSISREF3', 'DIAGNOSISREF4'] and v and v != '':
                    try:
                        processed[k] = int(v)
                    except ValueError:
                        processed[k] = v
            return processed
        return data