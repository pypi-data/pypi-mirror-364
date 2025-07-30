"""Utility functions for parsing CSV data values."""

from decimal import Decimal
from typing import Any, Optional


def decimal_or_none(value: Any) -> Optional[Decimal]:
    """Convert value to Decimal or None for empty/invalid values.
    
    Args:
        value: Input value to convert
        
    Returns:
        Decimal value or None if conversion fails or value is empty
    """
    if value is None or value == '' or value == 'NULL':
        return None
    
    if isinstance(value, Decimal):
        return value
        
    if isinstance(value, (int, float)):
        return Decimal(str(value))
        
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        try:
            return Decimal(value)
        except (ValueError, TypeError):
            return None
    
    return None


def int_or_none(value: Any) -> Optional[int]:
    """Convert value to int or None for empty/invalid values.
    
    Args:
        value: Input value to convert
        
    Returns:
        Integer value or None if conversion fails or value is empty
    """
    if value is None or value == '' or value == 'NULL':
        return None
    
    if isinstance(value, int):
        return value
        
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    if isinstance(value, float):
        return int(value)
    
    return None