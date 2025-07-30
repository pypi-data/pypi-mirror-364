"""Pydantic models for Synthea immunizations CSV format."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from .base import SyntheaBaseModel


class Immunization(SyntheaBaseModel):
    """Model representing a single immunization record from Synthea CSV output."""
    
    date: datetime = Field(alias='DATE', description="The date the immunization was administered")
    patient: UUID = Field(alias='PATIENT', description="Foreign key to the Patient")
    encounter: UUID = Field(alias='ENCOUNTER', description="Foreign key to the Encounter where the immunization was administered")
    code: str = Field(alias='CODE', description="Immunization code from CVX")
    description: str = Field(alias='DESCRIPTION', description="Description of the immunization")
    base_cost: Decimal = Field(alias='BASE_COST', description="The line item cost of the immunization")