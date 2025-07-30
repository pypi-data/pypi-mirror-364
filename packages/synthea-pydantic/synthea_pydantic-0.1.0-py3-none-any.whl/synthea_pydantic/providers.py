"""Pydantic models for Synthea providers CSV format."""

from typing import Literal, Optional
from uuid import UUID

from pydantic import Field

from .base import SyntheaBaseModel


class Provider(SyntheaBaseModel):
    """Model representing a single provider record from Synthea CSV output."""
    
    id: UUID = Field(alias='Id', description="Primary key of the Provider/Clinician")
    organization: UUID = Field(alias='ORGANIZATION', description="Foreign key to the Organization that employees this provider")
    name: str = Field(alias='NAME', description="First and last name of the Provider")
    gender: Literal["M", "F"] = Field(alias='GENDER', description="Gender. M is male, F is female")
    speciality: str = Field(alias='SPECIALITY', description="Provider speciality")
    address: str = Field(alias='ADDRESS', description="Provider's street address without commas or newlines")
    city: str = Field(alias='CITY', description="Street address city")
    state: Optional[str] = Field(None, alias='STATE', description="Street address state abbreviation")
    zip: Optional[str] = Field(None, alias='ZIP', description="Street address zip or postal code")
    lat: Optional[float] = Field(None, alias='LAT', description="Latitude of Provider's address")
    lon: Optional[float] = Field(None, alias='LON', description="Longitude of Provider's address")
    utilization: int = Field(alias='UTILIZATION', description="The number of encounters/procedures performed by this provider")