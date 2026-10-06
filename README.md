# DataFlow — Data Cleaning & Quality Automation Platform

> A production-minded Python automation platform for cleaning, validating, profiling, and reporting on customer datasets.

## Overview

DataFlow automates repetitive data-cleaning and quality-control workflows for CSV and Excel datasets.

Instead of manually reviewing inconsistent customer data, DataFlow applies a repeatable pipeline that standardizes records, validates critical fields, removes duplicate identifiers, generates quality reports, and provides a desktop interface for non-technical users.

The platform is designed with a modular architecture so the data-processing engine can be reused independently from the GUI.

## Key Capabilities

* CSV and XLSX input support
* Automatic whitespace normalization
* Status standardization
* Email validation
* Phone number normalization and validation
* Date format standardization
* Duplicate Customer ID removal
* Missing-value handling
* Data quality reporting
* Structured application logging
* Automated testing with pytest
* Desktop GUI built with CustomTkinter
* Original vs. cleaned dataset preview
* Dataset profiling and quality metrics
* Local processing for data privacy

## Processing Pipeline

```text
Input Dataset
     │
     ▼
File Loading
     │
     ▼
Schema & Text Normalization
     │
     ├── Email Validation
     ├── Phone Normalization
     ├── Phone Validation
     ├── Date Standardization
     └── Status Standardization
     │
     ▼
Duplicate Removal
     │
     ▼
Missing-Value Handling
     │
     ▼
Quality Analysis
     │
     ├── Cleaned Dataset
     ├── Quality Report
     └── Pipeline Logs
     │
     ▼
Final Output
```

## Architecture

```text
data/input/       → Raw datasets
        │
        ▼
src/cleaner.py    → Cleaning pipeline
src/validators.py → Field validation
src/reporter.py   → Quality reporting
src/main.py       → CLI pipeline orchestration
src/gui.py        → Desktop interface
        │
        ├── data/output/
        ├── reports/
        └── logs/
```

The processing logic is intentionally separated from the presentation layer. This allows the core cleaning engine to be executed through the command line or integrated into another interface without depending on the GUI.

## Project Structure

```text
python-data-cleaning-automation/
│
├── data/
│   ├── input/
│   └── output/
│
├── logs/
│   └── pipeline.log
│
├── reports/
│
├── src/
│   ├── cleaner.py
│   ├── gui.py
│   ├── main.py
│   ├── reporter.py
│   ├── validators.py
│   └── __init__.py
│
├── tests/
│   └── test_cleaning.py
│
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── requirements.txt
└── run_pipeline.py
```

## Technology Stack

| Technology    | Purpose                 |
| ------------- | ----------------------- |
| Python 3.10+  | Core application        |
| Pandas        | Dataset processing      |
| OpenPyXL      | Excel file support      |
| CustomTkinter | Desktop GUI             |
| Pytest        | Automated testing       |
| Logging       | Operational diagnostics |
| Git / GitHub  | Version control         |

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yussefmamoun11-hub/python-data-cleaning-automation.git
cd python-data-cleaning-automation
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

## Command-Line Usage

Place a CSV or XLSX dataset inside:

```text
data/input/
```

Run the pipeline:

```powershell
python run_pipeline.py
```

You can also provide a specific input file:

```powershell
python run_pipeline.py data/input/customers_january.csv
```

The pipeline generates:

```text
data/output/
reports/
logs/
```

## Desktop GUI

Launch the DataFlow desktop application:

```powershell
python src/gui.py
```

The GUI provides:

* File selection
* Dataset preview
* Data profiling
* Quality metrics
* Processing progress
* Quality report viewing
* Activity logs
* Output file access

## Testing

Run the complete automated test suite:

```powershell
python -m pytest
```

The test suite verifies core data-processing behavior including:

* Output generation
* Record counts
* Duplicate removal
* Missing-value handling
* Email validation
* Phone validation

## Data Privacy

DataFlow processes datasets locally on the user's machine.

Input files are not intentionally uploaded to an external service by the application.

Users should still follow their organization's data-handling, access-control, and retention policies when processing sensitive information.

## Quality Reporting

For each processed dataset, DataFlow can generate a quality report containing:

* Original record count
* Final record count
* Duplicate records removed
* Missing-value statistics
* Invalid email count
* Missing email count
* Invalid phone count
* Missing phone count
* Processing completion status

## Engineering Principles

The project follows several production-oriented principles:

* **Modularity** — processing, validation, reporting, and UI are separated.
* **Repeatability** — the same dataset can be processed through a consistent pipeline.
* **Observability** — pipeline activity is recorded through structured logs.
* **Testability** — core behavior is covered by automated tests.
* **Privacy by design** — processing occurs locally.
* **Maintainability** — functionality is organized into focused modules.

## Current Scope

DataFlow currently focuses on structured customer datasets and supports common data-quality operations.

It is not intended to replace enterprise-grade data-governance platforms or large-scale distributed data-processing systems.

## Roadmap

Potential future improvements include:

* Configurable validation rules
* Schema detection
* More advanced data-quality metrics
* Batch processing
* Export to additional formats
* Configuration files
* Improved test coverage
* CI/CD automation
* Packaged Windows executable
* Plugin-based validation rules

## License

This project is licensed under the MIT License. See `LICENSE` for details.

## Author

**Yussef Mamoun**

Cybersecurity undergraduate interested in security engineering, automation, and practical software solutions.

GitHub: `yussefmamoun11-hub`
