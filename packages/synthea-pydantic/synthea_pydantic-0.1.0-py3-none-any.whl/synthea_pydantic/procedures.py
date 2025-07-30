"""Pydantic models for Synthea procedures CSV format."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base import SyntheaBaseModel


class Procedure(SyntheaBaseModel):
    """Model representing a single procedure record from Synthea CSV output."""
    
    start: datetime = Field(alias='START', description="The date and time the procedure was performed")
    stop: Optional[datetime] = Field(None, alias='STOP', description="The date and time the procedure was completed, if applicable")
    patient: UUID = Field(alias='PATIENT', description="Foreign key to the Patient")
    encounter: UUID = Field(alias='ENCOUNTER', description="Foreign key to the Encounter where the procedure was performed")
    code: str = Field(alias='CODE', description="Procedure code from SNOMED-CT")
    description: str = Field(alias='DESCRIPTION', description="Description of the procedure")
    base_cost: Decimal = Field(alias='BASE_COST', description="The line item cost of the procedure")
    reasoncode: Optional[str] = Field(None, alias='REASONCODE', description="Diagnosis code from SNOMED-CT specifying why this procedure was performed")
    reasondescription: Optional[str] = Field(None, alias='REASONDESCRIPTION', description="Description of the reason code")