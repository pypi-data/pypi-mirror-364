# synthea-pydantic

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

Type-safe Pydantic models for parsing and validating [Synthea's](https://github.com/synthetichealth/synthea) synthetic healthcare data CSV exports.

## Overview

synthea-pydantic provides lightweight, type-annotated Pydantic models that make it easy to work with Synthea's CSV output format in Python. Synthea is a synthetic patient generator that creates realistic (but not real) patient health records for research, education, and software development.

### Key Features

- 🏥 **Complete Coverage**: Models for all 19 Synthea CSV export types
- 🔍 **Type Safety**: Full type annotations with proper validation
- 🚀 **Easy to Use**: Simple API that works with standard CSV libraries
- 📋 **Well Documented**: Comprehensive field descriptions from Synthea specifications
- 🔧 **Flexible**: Handles optional fields and empty values gracefully
- ⚡ **Lightweight**: Minimal dependencies (just Pydantic)

## Installation

```bash
pip install synthea-pydantic
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv pip install synthea-pydantic
```

## Quick Start

```python
import csv
from synthea_pydantic import Patient, Medication, Condition

# Load patients from CSV
with open('patients.csv') as f:
    reader = csv.DictReader(f)
    patients = [Patient(**row) for row in reader]

# Access patient data with full type safety
for patient in patients:
    print(f"{patient.first} {patient.last} - Born: {patient.birthdate}")
    if patient.deathdate:
        print(f"  Died: {patient.deathdate}")

# Load related data
with open('medications.csv') as f:
    reader = csv.DictReader(f)
    medications = [Medication(**row) for row in reader]

# Filter medications for a specific patient
patient_meds = [m for m in medications if m.patient == patient.id]
```

## Supported Models

synthea-pydantic includes models for all Synthea CSV export types:

| Model | Description | Key Fields |
|-------|-------------|------------|
| `Patient` | Patient demographics | id, birthdate, name, address, ssn |
| `Encounter` | Healthcare encounters | id, patient, start/stop, type, provider |
| `Condition` | Medical conditions | patient, code, description, onset |
| `Medication` | Prescriptions | patient, code, description, start/stop |
| `Observation` | Clinical observations | patient, code, value, units |
| `Procedure` | Medical procedures | patient, code, description, date |
| `Immunization` | Vaccination records | patient, code, date |
| `CarePlan` | Treatment plans | patient, code, activities |
| `Allergy` | Allergy records | patient, code, description |
| `Device` | Medical devices | patient, code, start/stop |
| `Supply` | Medical supplies | patient, code, quantity |
| `Organization` | Healthcare facilities | id, name, address, phone |
| `Provider` | Healthcare providers | id, name, speciality, organization |
| `Payer` | Insurance companies | id, name, ownership |
| `PayerTransition` | Insurance changes | patient, payer, start/stop |
| `Claim` | Insurance claims | id, patient, provider, total |
| `ClaimTransaction` | Claim line items | claim, type, amount |
| `ImagingStudy` | Medical imaging | patient, modality, body_site |

## Usage Examples

### Loading CSV Data

The models work with Python's built-in `csv` module:

```python
import csv
from synthea_pydantic import Patient

# Load from CSV file
with open('data/patients.csv') as f:
    reader = csv.DictReader(f)
    patients = [Patient(**row) for row in reader]
```

### Working with Optional Fields

Synthea CSVs often have empty values. The models handle these gracefully:

```python
# Empty strings in CSV are converted to None
patient = Patient(**{
    'Id': '123e4567-e89b-12d3-a456-426614174000',
    'BIRTHDATE': '1980-01-01',
    'DEATHDATE': '',  # Empty string becomes None
    'PREFIX': '',     # Empty string becomes None
    'FIRST': 'John',
    'LAST': 'Doe',
    # ... other required fields
})

assert patient.deathdate is None
assert patient.prefix is None
```

### Type Validation

All fields are validated according to their types:

```python
from decimal import Decimal
from datetime import date, datetime
from uuid import UUID

# UUIDs are automatically parsed
assert isinstance(patient.id, UUID)

# Dates are parsed from YYYY-MM-DD format
assert isinstance(patient.birthdate, date)

# Decimals maintain precision for monetary values
assert isinstance(patient.healthcare_expenses, Decimal)
```

### Linking Related Data

Use the UUID foreign keys to link related records:

```python
# Find all medications for a patient
patient_meds = [
    med for med in medications 
    if med.patient == patient.id
]

# Find all conditions treated in an encounter
encounter_conditions = [
    cond for cond in conditions 
    if cond.encounter == encounter.id
]
```

### Error Handling

The models provide clear error messages for invalid data:

```python
try:
    patient = Patient(**invalid_data)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

## Model Details

### Common Field Types

- **IDs**: UUID fields for primary and foreign keys
- **Dates**: `date` fields for dates (YYYY-MM-DD)
- **Timestamps**: `datetime` fields for date/time values
- **Money**: `Decimal` fields for monetary amounts
- **Codes**: String fields for medical codes (SNOMED-CT, RxNorm, etc.)

### Base Model Features

All models inherit from `SyntheaBaseModel` which provides:

- Automatic whitespace stripping
- Empty string to None conversion
- Case-insensitive literal field matching
- Field alias support for CSV column mapping

## Development

### Setup

To develop or contribute to synthea-pydantic:

```bash
# Clone the repository
git clone https://github.com/yourusername/synthea-pydantic.git
cd synthea-pydantic

# Install in development mode
uv pip install -e .
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=synthea_pydantic

# Run specific test file
uv run pytest tests/test_patients.py
```

### Code Quality

```bash
# Type checking
uv run mypy synthea_pydantic/

# Linting
uv run ruff check

# Formatting
uv run ruff format
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Synthea](https://github.com/synthetichealth/synthea) - The synthetic patient generator
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation using Python type annotations

## Resources

- [Synthea Documentation](https://github.com/synthetichealth/synthea/wiki)
- [Synthea CSV Format](https://github.com/synthetichealth/synthea/wiki/CSV-File-Data-Dictionary)
- [Sample Synthea Data](https://github.com/synthetichealth/synthea-sample-data)
