"""Pydantic models for Synthea supplies CSV format."""

from datetime import date as Date
from uuid import UUID

from pydantic import Field

from .base import SyntheaBaseModel


class Supply(SyntheaBaseModel):
    """Model representing a single supply record from Synthea CSV output."""
    
    date: Date = Field(alias='DATE', description="The date the supplies were used")
    patient: UUID = Field(alias='PATIENT', description="Foreign key to the Patient")
    encounter: UUID = Field(alias='ENCOUNTER', description="Foreign key to the Encounter when the supplies were used")
    code: str = Field(alias='CODE', description="Code for the type of supply used, from SNOMED-CT")
    description: str = Field(alias='DESCRIPTION', description="Description of supply used")
    quantity: int = Field(alias='QUANTITY', description="Quantity of supply used")