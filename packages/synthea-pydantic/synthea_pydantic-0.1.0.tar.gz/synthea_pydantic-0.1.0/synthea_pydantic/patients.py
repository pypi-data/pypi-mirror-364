"""Pydantic models for Synthea patients CSV format."""

from datetime import date
from decimal import Decimal
from typing import Literal, Optional
from uuid import UUID

from pydantic import Field

from .base import SyntheaBaseModel


class Patient(SyntheaBaseModel):
    """Model representing a single patient record from Synthea CSV output."""
    
    id: UUID = Field(alias='Id', description="Primary Key. Unique Identifier of the patient")
    birthdate: date = Field(alias='BIRTHDATE', description="The date the patient was born")
    deathdate: Optional[date] = Field(None, alias='DEATHDATE', description="The date the patient died")
    ssn: str = Field(alias='SSN', description="Patient Social Security identifier")
    drivers: Optional[str] = Field(None, alias='DRIVERS', description="Patient Drivers License identifier")
    passport: Optional[str] = Field(None, alias='PASSPORT', description="Patient Passport identifier")
    prefix: Optional[str] = Field(None, alias='PREFIX', description="Name prefix, such as Mr., Mrs., Dr., etc")
    first: str = Field(alias='FIRST', description="First name of the patient")
    last: str = Field(alias='LAST', description="Last or surname of the patient")
    suffix: Optional[str] = Field(None, alias='SUFFIX', description="Name suffix, such as PhD, MD, JD, etc")
    maiden: Optional[str] = Field(None, alias='MAIDEN', description="Maiden name of the patient")
    marital: Optional[Literal["M", "S"]] = Field(None, alias='MARITAL', description="Marital Status. M is married, S is single. Currently no support for divorce (D) or widowing (W)")
    race: str = Field(alias='RACE', description="Description of the patient's primary race")
    ethnicity: str = Field(alias='ETHNICITY', description="Description of the patient's primary ethnicity")
    gender: Literal["M", "F"] = Field(alias='GENDER', description="Gender. M is male, F is female")
    birthplace: str = Field(alias='BIRTHPLACE', description="Name of the town where the patient was born")
    address: str = Field(alias='ADDRESS', description="Patient's street address without commas or newlines")
    city: str = Field(alias='CITY', description="Patient's address city")
    state: str = Field(alias='STATE', description="Patient's address state")
    county: Optional[str] = Field(None, alias='COUNTY', description="Patient's address county")
    zip: Optional[str] = Field(None, alias='ZIP', description="Patient's zip code")
    lat: Optional[Decimal] = Field(None, alias='LAT', description="Latitude of Patient's address")
    lon: Optional[Decimal] = Field(None, alias='LON', description="Longitude of Patient's address")
    healthcare_expenses: Decimal = Field(alias='HEALTHCARE_EXPENSES', description="The total lifetime cost of healthcare to the patient (i.e. what the patient paid)")
    healthcare_coverage: Decimal = Field(alias='HEALTHCARE_COVERAGE', description="The total lifetime cost of healthcare services that were covered by Payers (i.e. what the insurance company paid)")