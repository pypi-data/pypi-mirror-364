"""Pydantic models for Synthea allergies CSV format."""

from datetime import date
from typing import Literal, Optional
from uuid import UUID

from pydantic import Field

from .base import SyntheaBaseModel


class Allergy(SyntheaBaseModel):
    """Model representing a single allergy record from Synthea CSV output."""
    
    start: date = Field(alias='START', description="The date the allergy was diagnosed")
    stop: Optional[date] = Field(None, alias='STOP', description="The date the allergy ended, if applicable")
    patient: UUID = Field(alias='PATIENT', description="Foreign key to the Patient")
    encounter: UUID = Field(alias='ENCOUNTER', description="Foreign key to the Encounter when the allergy was diagnosed")
    code: str = Field(alias='CODE', description="Allergy code")
    system: str = Field(alias='SYSTEM', description="Terminology system of the Allergy code. RxNorm if this is a medication allergy, otherwise SNOMED-CT")
    description: str = Field(alias='DESCRIPTION', description="Description of the Allergy")
    type: Optional[Literal["allergy", "intolerance"]] = Field(None, alias='TYPE', description="Identify entry as an allergy or intolerance")
    category: Optional[Literal["drug", "medication", "food", "environment"]] = Field(None, alias='CATEGORY', description="Identify the category")
    reaction1: Optional[str] = Field(None, alias='REACTION1', description="Optional SNOMED code of the patients reaction")
    description1: Optional[str] = Field(None, alias='DESCRIPTION1', description="Optional description of the Reaction1 SNOMED code")
    severity1: Optional[Literal["MILD", "MODERATE", "SEVERE"]] = Field(None, alias='SEVERITY1', description="Severity of the reaction")
    reaction2: Optional[str] = Field(None, alias='REACTION2', description="Optional SNOMED code of the patients second reaction")
    description2: Optional[str] = Field(None, alias='DESCRIPTION2', description="Optional description of the Reaction2 SNOMED code")
    severity2: Optional[Literal["MILD", "MODERATE", "SEVERE"]] = Field(None, alias='SEVERITY2', description="Severity of the second reaction")