import pandas as pd

from validators import (
    validate_email,
    clean_phone,
    validate_phone,
    standardize_date
)


def load_dataset(input_file):
    if input_file.lower().endswith(".xlsx"):
        return pd.read_excel(input_file)

    if input_file.lower().endswith(".csv"):
        return pd.read_csv(input_file)

    raise ValueError(
        "Unsupported file format. Use CSV or XLSX."
    )


def clean_dataset(input_file):
    df = load_dataset(input_file)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Clean text columns
    text_columns = [
        "Name",
        "Email",
        "Phone",
        "City",
        "Status"
    ]

    for column in text_columns:
        if column in df.columns:
            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    # Standardize status
    if "Status" in df.columns:
        df["Status"] = df["Status"].str.capitalize()

    # Email validation
    if "Email" in df.columns:
        df["Email Status"] = df["Email"].apply(
            validate_email
        )

    # Phone cleaning and validation
    if "Phone" in df.columns:
        df["Phone"] = df["Phone"].apply(clean_phone)

        df["Phone Status"] = df["Phone"].apply(
            validate_phone
        )

    # Date standardization
    if "Registration Date" in df.columns:
        df["Registration Date"] = (
            df["Registration Date"]
            .apply(standardize_date)
            .dt.strftime("%Y-%m-%d")
        )

    # Remove duplicate Customer IDs
    if "Customer ID" in df.columns:
        df = df.drop_duplicates(
            subset=["Customer ID"],
            keep="first"
        )

    # Handle missing City
    if "City" in df.columns:
        df["City"] = df["City"].fillna("Unknown")

    return df
