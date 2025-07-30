"""Pydantic models for Synthea devices CSV format."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base import SyntheaBaseModel


class Device(SyntheaBaseModel):
    """Model representing a single device record from Synthea CSV output."""
    
    start: datetime = Field(alias='START', description="The date and time the device was associated to the patient")
    stop: Optional[datetime] = Field(None, alias='STOP', description="The date and time the device was removed, if applicable")
    patient: UUID = Field(alias='PATIENT', description="Foreign key to the Patient")
    encounter: UUID = Field(alias='ENCOUNTER', description="Foreign key to the Encounter when the device was associated")
    code: str = Field(alias='CODE', description="Type of device, from SNOMED-CT")
    description: str = Field(alias='DESCRIPTION', description="Description of the device")
    udi: str = Field(alias='UDI', description="Unique Device Identifier for the device")