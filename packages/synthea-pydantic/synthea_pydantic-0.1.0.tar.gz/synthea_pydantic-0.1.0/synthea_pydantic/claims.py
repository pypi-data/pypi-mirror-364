"""Pydantic models for Synthea claims CSV format."""

from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional
from uuid import UUID

from pydantic import Field, model_validator

from .base import SyntheaBaseModel


class Claim(SyntheaBaseModel):
    """Model representing a single claim record from Synthea CSV output."""
    
    id: UUID = Field(alias='Id', description="Primary Key. Unique Identifier of the claim")
    patientid: UUID = Field(alias='PATIENTID', description="Foreign key to the Patient")
    providerid: UUID = Field(alias='PROVIDERID', description="Foreign key to the Provider")
    primarypatientinsuranceid: Optional[UUID] = Field(None, alias='PRIMARYPATIENTINSURANCEID', description="Foreign key to the primary Payer")
    secondarypatientinsuranceid: Optional[UUID] = Field(None, alias='SECONDARYPATIENTINSURANCEID', description="Foreign key to the second Payer")
    departmentid: int = Field(alias='DEPARTMENTID', description="Placeholder for department")
    patientdepartmentid: int = Field(alias='PATIENTDEPARTMENTID', description="Placeholder for patient department")
    diagnosis1: Optional[str] = Field(None, alias='DIAGNOSIS1', description="SNOMED-CT code corresponding to a diagnosis related to the claim")
    diagnosis2: Optional[str] = Field(None, alias='DIAGNOSIS2', description="SNOMED-CT code corresponding to a diagnosis related to the claim")
    diagnosis3: Optional[str] = Field(None, alias='DIAGNOSIS3', description="SNOMED-CT code corresponding to a diagnosis related to the claim")
    diagnosis4: Optional[str] = Field(None, alias='DIAGNOSIS4', description="SNOMED-CT code corresponding to a diagnosis related to the claim")
    diagnosis5: Optional[str] = Field(None, alias='DIAGNOSIS5', description="SNOMED-CT code corresponding to a diagnosis related to the claim")
    diagnosis6: Optional[str] = Field(None, alias='DIAGNOSIS6', description="SNOMED-CT code corresponding to a diagnosis related to the claim")
    diagnosis7: Optional[str] = Field(None, alias='DIAGNOSIS7', description="SNOMED-CT code corresponding to a diagnosis related to the claim")
    diagnosis8: Optional[str] = Field(None, alias='DIAGNOSIS8', description="SNOMED-CT code corresponding to a diagnosis related to the claim")
    referringproviderid: Optional[UUID] = Field(None, alias='REFERRINGPROVIDERID', description="Foreign key to the Provider who made the referral")
    appointmentid: Optional[UUID] = Field(None, alias='APPOINTMENTID', description="Foreign key to the Encounter")
    currentillnessdate: datetime = Field(alias='CURRENTILLNESSDATE', description="The date the patient experienced symptoms")
    servicedate: datetime = Field(alias='SERVICEDATE', description="The date of the services on the claim")
    supervisingproviderid: Optional[UUID] = Field(None, alias='SUPERVISINGPROVIDERID', description="Foreign key to the supervising Provider")
    status1: Optional[Literal["BILLED", "CLOSED"]] = Field(None, alias='STATUS1', description="Status of the claim from the Primary Insurance. BILLED or CLOSED")
    status2: Optional[Literal["BILLED", "CLOSED"]] = Field(None, alias='STATUS2', description="Status of the claim from the Secondary Insurance. BILLED or CLOSED")
    statusp: Optional[Literal["BILLED", "CLOSED"]] = Field(None, alias='STATUSP', description="Status of the claim from the Patient. BILLED or CLOSED")
    outstanding1: Optional[Decimal] = Field(None, alias='OUTSTANDING1', description="Total amount of money owed by Primary Insurance")
    outstanding2: Optional[Decimal] = Field(None, alias='OUTSTANDING2', description="Total amount of money owed by Secondary Insurance")
    outstandingp: Optional[Decimal] = Field(None, alias='OUTSTANDINGP', description="Total amount of money owed by Patient")
    lastbilleddate1: Optional[datetime] = Field(None, alias='LASTBILLEDDATE1', description="Date the claim was sent to Primary Insurance")
    lastbilleddate2: Optional[datetime] = Field(None, alias='LASTBILLEDDATE2', description="Date the claim was sent to Secondary Insurance")
    lastbilleddatep: Optional[datetime] = Field(None, alias='LASTBILLEDDATEP', description="Date the claim was sent to the Patient")
    healthcareclaimtypeid1: Optional[Literal[1, 2]] = Field(None, alias='HEALTHCARECLAIMTYPEID1', description="Type of claim: 1 is professional, 2 is institutional")
    healthcareclaimtypeid2: Optional[Literal[1, 2]] = Field(None, alias='HEALTHCARECLAIMTYPEID2', description="Type of claim: 1 is professional, 2 is institutional")
    healthcareclaimtypeidp: Optional[str] = Field(None, alias='HEALTHCARECLAIMTYPEIDP', description="Healthcare claim type ID for patient")
    
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
                if k in ['SECONDARYPATIENTINSURANCEID', 'PRIMARYPATIENTINSURANCEID'] and v == '0':
                    processed[k] = None
                # Handle '0' as None for claim type IDs
                elif k in ['HEALTHCARECLAIMTYPEID1', 'HEALTHCARECLAIMTYPEID2'] and v == '0':
                    processed[k] = None
                # Convert string numbers to integers for claim type IDs
                elif k in ['HEALTHCARECLAIMTYPEID1', 'HEALTHCARECLAIMTYPEID2'] and v and v != '0':
                    try:
                        processed[k] = int(v)
                    except ValueError:
                        processed[k] = v
            return processed
        return data