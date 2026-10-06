# Python Data Cleaning Automation

A reusable Python automation pipeline for cleaning, validating, testing, and reporting data quality from CSV and Excel datasets.

## Overview

This project automates common data-cleaning tasks that are frequently required before analysis, reporting, CRM imports, or business operations.

Instead of manually cleaning spreadsheets, the pipeline processes the dataset automatically and generates a cleaned output, validation results, quality report, and execution log.

## What It Does

The pipeline can:

- Load CSV and Excel files
- Clean column names
- Remove unnecessary text spaces
- Standardize status values
- Validate email addresses
- Normalize and validate phone numbers
- Standardize dates
- Remove duplicate customer records
- Handle missing city values
- Generate a data quality report
- Generate execution logs
- Run automated tests
- Accept custom input files
- Produce consistent cleaned output

## Pipeline

Input Dataset
       ?
Data Loading
       ?
Data Cleaning
       ?
Data Validation
       ?
Duplicate Removal
       ?
Missing Value Handling
       ?
Quality Report
       ?
Cleaned Dataset
       ?
Automated Tests

## Project Structure

python-data-cleaning-automation/
¦
+-- data/
¦   +-- input/
¦   ¦   +-- customers_january.csv
¦   +-- output/
¦
+-- reports/
¦
+-- logs/
¦
+-- src/
¦   +-- __init__.py
¦   +-- main.py
¦   +-- cleaner.py
¦   +-- validators.py
¦   +-- reporter.py
¦
+-- tests/
¦   +-- test_cleaning.py
¦
+-- .gitignore
+-- requirements.txt
+-- run_pipeline.py
+-- README.md

## Example Dataset

The included sample dataset intentionally contains common data-quality problems:

- Duplicate Customer ID
- Missing email
- Invalid email addresses
- Missing phone number
- Invalid phone number
- Inconsistent status capitalization
- Different date formats
- Missing city
- Extra spaces in text fields

## Example Results

Original records: 10

Final records: 9

Duplicates removed: 1

Invalid emails: 2

Missing emails: 1

Invalid phones: 1

Missing phones: 1

All automated tests: PASSED

## Installation

Clone the repository and enter the project directory.

Create a virtual environment:

    python -m venv .venv

Activate it on Windows:

    .venv\Scripts\Activate.ps1

Install dependencies:

    pip install -r requirements.txt

## Run the Pipeline

Run the complete automation:

    python run_pipeline.py

The pipeline will:

1. Clean the dataset
2. Generate the cleaned CSV
3. Generate the quality report
4. Generate the execution log
5. Run automated tests

## Process a Custom File

CSV:

    python src/main.py data/input/customers_january.csv

Excel:

    python src/main.py data/input/customers_january.xlsx

Supported formats:

- CSV
- XLSX

## Testing

Run the complete test suite:

    python -m pytest -v

Current test coverage includes:

- Output file creation
- Row count validation
- Duplicate Customer ID detection
- Missing city validation
- Email validation
- Phone validation

## Technologies

- Python
- Pandas
- OpenPyXL
- Pytest
- Regular Expressions
- CSV
- Excel
- Python Logging

## Use Cases

This automation can be adapted for:

- Customer databases
- CRM imports
- Sales datasets
- Marketing lists
- Contact databases
- Business spreadsheets
- Data migration
- Reporting preparation
- Freelance data-cleaning tasks

## Future Improvements

Potential extensions include:

- Excel output generation
- Multiple input files
- Advanced validation rules
- Configurable cleaning rules
- HTML reports
- Data-quality scoring
- Web interface
- Scheduled automation
- Database integration

## Author

Yussef Mamoun

Cybersecurity Student | Python Automation | Data Processing

## License

This project is intended for educational, portfolio, and freelance automation use.
