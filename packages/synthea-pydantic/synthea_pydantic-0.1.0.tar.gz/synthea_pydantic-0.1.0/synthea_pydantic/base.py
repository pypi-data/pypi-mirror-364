"""Base model for all Synthea CSV models."""

from decimal import Decimal
from typing import Union, get_origin, get_args

from pydantic import BaseModel, ConfigDict, model_validator, field_validator

from typing_extensions import Literal

from ._parsers import decimal_or_none


class SyntheaBaseModel(BaseModel):
    """Base model with common configuration and validation for all Synthea CSV models."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        populate_by_name=True,  # Accept both field name and alias
    )
    
    @model_validator(mode='before')
    @classmethod
    def preprocess_csv(cls, data):
        """Convert empty strings to None and apply field coercions."""
        if isinstance(data, dict):
            processed = {}
            for k, v in data.items():
                # Convert empty strings to None
                if v == '':
                    processed[k] = None
                    continue
                
                # Apply case normalization for Literal string fields
                processed[k] = cls._normalize_literal_field(k, v)
            return processed
        return data
    
    @classmethod
    def _normalize_literal_field(cls, field_name: str, value):
        """Normalize string values for Literal fields to uppercase."""
        if not isinstance(value, str):
            return value
            
        # Get field info from model annotations
        field_info = None
        for name, field in cls.model_fields.items():
            if field.alias == field_name or name == field_name:
                field_info = field
                break
        
        if not field_info:
            return value
            
        # Check if this is a Literal field with string values
        annotation = field_info.annotation
        literal_values = None
        
        # Handle Optional[Literal[...]] and Union[Literal[...], None]
        if get_origin(annotation) is Union:
            args = get_args(annotation)
            # Look for a Literal type in the Union
            for arg in args:
                if get_origin(arg) is Literal:
                    literal_values = get_args(arg)
                    break
        elif get_origin(annotation) is Literal:
            literal_values = get_args(annotation)
        
        # If we found Literal values, try case normalization
        if literal_values and all(isinstance(val, str) for val in literal_values):
            # Check if the original case-sensitive value matches first
            if value in literal_values:
                return value
            
            # Try case-insensitive matching
            value_lower = value.lower()
            for literal_val in literal_values:
                if literal_val.lower() == value_lower:
                    return literal_val
        
        return value
    
    @field_validator('*', mode='before')
    @classmethod
    def validate_decimal_fields(cls, value, info):
        """Apply decimal_or_none to all Decimal fields."""
        # Get the field info for this field
        field_name = info.field_name
        if field_name not in cls.model_fields:
            return value
            
        field_info = cls.model_fields[field_name]
        annotation = field_info.annotation
        
        # Check if this is a Decimal field (including Optional[Decimal])
        is_decimal = False
        if annotation is Decimal:
            is_decimal = True
        elif get_origin(annotation) is Union:
            args = get_args(annotation)
            # Check if Decimal is in the Union (for Optional[Decimal])
            if Decimal in args:
                is_decimal = True
        
        if is_decimal:
            return decimal_or_none(value)
        
        return value