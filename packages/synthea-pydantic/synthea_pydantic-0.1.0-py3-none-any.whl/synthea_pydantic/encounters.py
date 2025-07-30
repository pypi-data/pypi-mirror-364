"""Pydantic models for Synthea encounters CSV format."""

from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional
from uuid import UUID

from pydantic import Field

from .base import SyntheaBaseModel


class Encounter(SyntheaBaseModel):
    """Model representing a single encounter record from Synthea CSV output."""
    
    id: UUID = Field(alias='Id', description="Primary Key. Unique Identifier of the encounter")
    start: datetime = Field(alias='START', description="The date and time the encounter started")
    stop: Optional[datetime] = Field(None, alias='STOP', description="The date and time the encounter concluded")
    patient: UUID = Field(alias='PATIENT', description="Foreign key to the Patient")
    organization: UUID = Field(alias='ORGANIZATION', description="Foreign key to the Organization")
    provider: UUID = Field(alias='PROVIDER', description="Foreign key to the Provider")
    payer: UUID = Field(alias='PAYER', description="Foreign key to the Payer")
    encounterclass: Literal["ambulatory", "emergency", "inpatient", "wellness", "urgentcare", "outpatient"] = Field(alias='ENCOUNTERCLASS', description="The class of the encounter, such as ambulatory, emergency, inpatient, wellness, urgentcare, or outpatient")
    code: str = Field(alias='CODE', description="Encounter code from SNOMED-CT")
    description: str = Field(alias='DESCRIPTION', description="Description of the type of encounter")
    base_encounter_cost: Decimal = Field(alias='BASE_ENCOUNTER_COST', description="The base cost of the encounter, not including any line item costs related to medications, immunizations, procedures, or other services")
    total_claim_cost: Decimal = Field(alias='TOTAL_CLAIM_COST', description="The total cost of the encounter, including all line items")
    payer_coverage: Decimal = Field(alias='PAYER_COVERAGE', description="The amount of cost covered by the Payer")
    reasoncode: Optional[str] = Field(None, alias='REASONCODE', description="Diagnosis code from SNOMED-CT, only if this encounter targeted a specific condition")
    reasondescription: Optional[str] = Field(None, alias='REASONDESCRIPTION', description="Description of the reason code")