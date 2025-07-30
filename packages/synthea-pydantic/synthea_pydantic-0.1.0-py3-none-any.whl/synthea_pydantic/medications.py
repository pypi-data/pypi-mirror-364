"""Pydantic models for Synthea medications CSV format."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base import SyntheaBaseModel


class Medication(SyntheaBaseModel):
    """Model representing a single medication record from Synthea CSV output."""
    
    start: datetime = Field(alias='START', description="The date and time the medication was prescribed")
    stop: Optional[datetime] = Field(None, alias='STOP', description="The date and time the prescription ended, if applicable")
    patient: UUID = Field(alias='PATIENT', description="Foreign key to the Patient")
    payer: UUID = Field(alias='PAYER', description="Foreign key to the Payer")
    encounter: UUID = Field(alias='ENCOUNTER', description="Foreign key to the Encounter where the medication was prescribed")
    code: str = Field(alias='CODE', description="Medication code from RxNorm")
    description: str = Field(alias='DESCRIPTION', description="Description of the medication")
    base_cost: Decimal = Field(alias='BASE_COST', description="The line item cost of the medication")
    payer_coverage: Decimal = Field(alias='PAYER_COVERAGE', description="The amount covered or reimbursed by the Payer")
    dispenses: int = Field(alias='DISPENSES', description="The number of times the prescription was filled")
    totalcost: Decimal = Field(alias='TOTALCOST', description="The total cost of the prescription, including all dispenses")
    reasoncode: Optional[str] = Field(None, alias='REASONCODE', description="Diagnosis code from SNOMED-CT specifying why this medication was prescribed")
    reasondescription: Optional[str] = Field(None, alias='REASONDESCRIPTION', description="Description of the reason code")