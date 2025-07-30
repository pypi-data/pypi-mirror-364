"""Pydantic models for Synthea payers CSV format."""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base import SyntheaBaseModel


class Payer(SyntheaBaseModel):
    """Model representing a single payer record from Synthea CSV output."""
    
    id: UUID = Field(alias='Id', description="Primary Key")
    name: str = Field(alias='NAME', description="Name of the payer")
    address: Optional[str] = Field(None, alias='ADDRESS', description="Payer's street address without commas or newlines")
    city: Optional[str] = Field(None, alias='CITY', description="Street address city")
    state_headquartered: Optional[str] = Field(None, alias='STATE_HEADQUARTERED', description="Street address state abbreviation")
    zip: Optional[str] = Field(None, alias='ZIP', description="Street address zip or postal code")
    phone: Optional[str] = Field(None, alias='PHONE', description="Payer's phone number")
    amount_covered: Decimal = Field(alias='AMOUNT_COVERED', description="The monetary amount paid to Organizations during the entire simulation")
    amount_uncovered: Decimal = Field(alias='AMOUNT_UNCOVERED', description="The monetary amount not paid to Organizations during the entire simulation, and covered out of pocket by patients")
    revenue: Decimal = Field(alias='REVENUE', description="The monetary revenue of the Payer during the entire simulation")
    covered_encounters: int = Field(alias='COVERED_ENCOUNTERS', description="Number of encounter costs covered by the Payer")
    uncovered_encounters: int = Field(alias='UNCOVERED_ENCOUNTERS', description="Number of encounter costs not covered by the Payer")
    covered_medications: int = Field(alias='COVERED_MEDICATIONS', description="Number of medication costs covered by the Payer")
    uncovered_medications: int = Field(alias='UNCOVERED_MEDICATIONS', description="Number of medication costs not covered by the Payer")
    covered_procedures: int = Field(alias='COVERED_PROCEDURES', description="Number of procedure costs covered by the Payer")
    uncovered_procedures: int = Field(alias='UNCOVERED_PROCEDURES', description="Number of procedure costs not covered by the Payer")
    covered_immunizations: int = Field(alias='COVERED_IMMUNIZATIONS', description="Number of immunization costs covered by the Payer")
    uncovered_immunizations: int = Field(alias='UNCOVERED_IMMUNIZATIONS', description="Number of immunization costs not covered by the Payer")
    unique_customers: int = Field(alias='UNIQUE_CUSTOMERS', description="Number of unique patients enrolled with the Payer")
    qols_avg: float = Field(alias='QOLS_AVG', description="Average patient's Quality of Life scores for those enrolled in the Payer during the entire simulation")
    member_months: int = Field(alias='MEMBER_MONTHS', description="The total number of months that patients were enrolled with this Payer during the simulation and paid monthly premiums (if any)")