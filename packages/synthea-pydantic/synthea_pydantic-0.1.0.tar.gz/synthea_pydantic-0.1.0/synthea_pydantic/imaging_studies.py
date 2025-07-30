"""Pydantic models for Synthea imaging_studies CSV format."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base import SyntheaBaseModel


class ImagingStudy(SyntheaBaseModel):
    """Model representing a single imaging study record from Synthea CSV output."""
    
    id: UUID = Field(alias='Id', description="Non-unique identifier of the imaging study. An imaging study may have multiple rows.")
    date: datetime = Field(alias='DATE', description="The date and time the imaging study was conducted")
    patient: UUID = Field(alias='PATIENT', description="Foreign key to the Patient")
    encounter: UUID = Field(alias='ENCOUNTER', description="Foreign key to the Encounter")
    series_uid: str = Field(alias='SERIES_UID', description="Imaging Study series DICOM UID.")
    bodysite_code: str = Field(alias='BODYSITE_CODE', description="A SNOMED Body Structures code describing what part of the body the images in the series were taken of.")
    bodysite_description: str = Field(alias='BODYSITE_DESCRIPTION', description="Description of the body site")
    modality_code: str = Field(alias='MODALITY_CODE', description="A DICOM-DCM code describing the method used to take the images.")
    modality_description: str = Field(alias='MODALITY_DESCRIPTION', description="Description of the image modality")
    instance_uid: str = Field(alias='INSTANCE_UID', description="Imaging Study instance DICOM UID.")
    sop_code: str = Field(alias='SOP_CODE', description="A DICOM-SOP code describing the Subject-Object Pair (SOP) that constitutes the image.")
    sop_description: str = Field(alias='SOP_DESCRIPTION', description="Description of the SOP code")
    procedure_code: str = Field(alias='PROCEDURE_CODE', description="Imaging Procedure code from SNOMED-CT")
    instance_number: Optional[int] = Field(None, alias='INSTANCE_NUMBER', description="Number of the instance within the series")
    description: Optional[str] = Field(None, alias='DESCRIPTION', description="Description of the imaging study")