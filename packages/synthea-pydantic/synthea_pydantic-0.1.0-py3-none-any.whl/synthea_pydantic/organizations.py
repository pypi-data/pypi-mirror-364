"""Pydantic models for Synthea organizations CSV format."""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base import SyntheaBaseModel


class Organization(SyntheaBaseModel):
    """Model representing a single organization record from Synthea CSV output."""
    
    id: UUID = Field(alias='Id', description="Primary key of the Organization")
    name: str = Field(alias='NAME', description="Name of the Organization")
    address: str = Field(alias='ADDRESS', description="Organization's street address without commas or newlines")
    city: str = Field(alias='CITY', description="Street address city")
    state: Optional[str] = Field(None, alias='STATE', description="Street address state abbreviation")
    zip: Optional[str] = Field(None, alias='ZIP', description="Street address zip or postal code")
    lat: Optional[float] = Field(None, alias='LAT', description="Latitude of Organization's address")
    lon: Optional[float] = Field(None, alias='LON', description="Longitude of Organization's address")
    phone: Optional[str] = Field(None, alias='PHONE', description="Organization's phone number. Sometimes multiple numbers")
    revenue: Decimal = Field(alias='REVENUE', description="The monetary revenue of the organization during the entire simulation")
    utilization: int = Field(alias='UTILIZATION', description="The number of Encounters performed by this Organization")