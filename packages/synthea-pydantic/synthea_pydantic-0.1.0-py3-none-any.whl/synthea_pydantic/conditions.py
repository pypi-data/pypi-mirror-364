"""Pydantic models for Synthea conditions CSV format."""

from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base import SyntheaBaseModel


class Condition(SyntheaBaseModel):
    """Model representing a single condition record from Synthea CSV output."""
    
    start: date = Field(alias='START', description="The date the condition was diagnosed")
    stop: Optional[date] = Field(None, alias='STOP', description="The date the condition resolved, if applicable")
    patient: UUID = Field(alias='PATIENT', description="Foreign key to the Patient")
    encounter: UUID = Field(alias='ENCOUNTER', description="Foreign key to the Encounter when the condition was diagnosed")
    code: str = Field(alias='CODE', description="Diagnosis code from SNOMED-CT")
    description: str = Field(alias='DESCRIPTION', description="Description of the condition")