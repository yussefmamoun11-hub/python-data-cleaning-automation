import os
import pandas as pd


def generate_quality_report(
    original_file,
    cleaned_df,
    report_file
):
    original_df = pd.read_csv(
        original_file
    )

    original_rows = len(original_df)
    cleaned_rows = len(cleaned_df)

    duplicates_removed = (
        original_rows - cleaned_rows
    )

    missing_values = original_df.isnull().sum()
    total_missing = missing_values.sum()

    invalid_emails = 0
    missing_emails = 0
    invalid_phones = 0
    missing_phones = 0

    if "Email Status" in cleaned_df.columns:
        invalid_emails = (
            cleaned_df["Email Status"] == "Invalid"
        ).sum()

        missing_emails = (
            cleaned_df["Email Status"] == "Missing"
        ).sum()

    if "Phone Status" in cleaned_df.columns:
        invalid_phones = (
            cleaned_df["Phone Status"] == "Invalid"
        ).sum()

        missing_phones = (
            cleaned_df["Phone Status"] == "Missing"
        ).sum()

    report = f"""
========================================
       DATA QUALITY REPORT
========================================

Dataset: {os.path.basename(original_file)}

--- RECORD SUMMARY ---

Original records: {original_rows}
Final records: {cleaned_rows}
Duplicates removed: {duplicates_removed}

--- MISSING VALUES ---

Total missing values: {total_missing}

"""

    for column, count in missing_values.items():
        report += f"{column}: {count}\n"

    report += f"""
--- EMAIL QUALITY ---

Invalid emails: {invalid_emails}
Missing emails: {missing_emails}

--- PHONE QUALITY ---

Invalid phones: {invalid_phones}
Missing phones: {missing_phones}

--- FINAL STATUS ---

Cleaning completed successfully.

========================================
"""

    os.makedirs(
        os.path.dirname(report_file),
        exist_ok=True
    )

    with open(
        report_file,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(report)

    return report
