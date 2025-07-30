"""Pydantic models for Synthea careplans CSV format."""

from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base import SyntheaBaseModel


class CarePlan(SyntheaBaseModel):
    """Model representing a single care plan record from Synthea CSV output."""
    
    id: UUID = Field(alias='Id', description="Primary Key. Unique Identifier of the care plan")
    start: date = Field(alias='START', description="The date the care plan was initiated")
    stop: Optional[date] = Field(None, alias='STOP', description="The date the care plan ended, if applicable")
    patient: UUID = Field(alias='PATIENT', description="Foreign key to the Patient")
    encounter: UUID = Field(alias='ENCOUNTER', description="Foreign key to the Encounter when the care plan was initiated")
    code: str = Field(alias='CODE', description="Code from SNOMED-CT")
    description: str = Field(alias='DESCRIPTION', description="Description of the care plan")
    reasoncode: Optional[str] = Field(None, alias='REASONCODE', description="Diagnosis code from SNOMED-CT that this care plan addresses")
    reasondescription: Optional[str] = Field(None, alias='REASONDESCRIPTION', description="Description of the reason code")