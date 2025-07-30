"""Pydantic models for Synthea observations CSV format."""

from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from pydantic import Field, model_validator

from .base import SyntheaBaseModel


class Observation(SyntheaBaseModel):
    """Model representing a single observation record from Synthea CSV output."""
    
    date: datetime = Field(alias='DATE', description="The date and time the observation was performed")
    patient: UUID = Field(alias='PATIENT', description="Foreign key to the Patient")
    encounter: Optional[UUID] = Field(None, alias='ENCOUNTER', description="Foreign key to the Encounter where the observation was performed")
    category: Optional[str] = Field(None, alias='CATEGORY', description="Category of the observation")
    code: str = Field(alias='CODE', description="Observation or Lab code from LOINC")
    description: str = Field(alias='DESCRIPTION', description="Description of the observation")
    value: Optional[Union[str, float]] = Field(None, alias='VALUE', description="The recorded value of the observation. Often numeric, but some values can be verbose, for example, multiple-choice questionnaire responses")
    units: Optional[str] = Field(None, alias='UNITS', description="The units of measure for the value, if applicable")
    type: str = Field(alias='TYPE', description="The datatype of value: text or numeric")
    
    @model_validator(mode='before')
    @classmethod
    def preprocess_csv(cls, data):
        """Convert empty strings to None and handle numeric values."""
        # First apply the base preprocessing
        data = super().preprocess_csv(data)
        
        if isinstance(data, dict):
            processed = data.copy()
            # Try to convert numeric values in VALUE field when TYPE is numeric
            if processed.get('TYPE') == 'numeric' and processed.get('VALUE'):
                try:
                    processed['VALUE'] = float(processed['VALUE'])
                except ValueError:
                    pass  # Keep original value if conversion fails
            return processed
        return data