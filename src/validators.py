import pandas as pd
import re


EMAIL_PATTERN = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"


def validate_email(email):
    if pd.isna(email) or str(email).strip() == "":
        return "Missing"

    if re.match(EMAIL_PATTERN, str(email)):
        return "Valid"

    return "Invalid"


def clean_phone(phone):
    if pd.isna(phone) or str(phone).strip() == "":
        return pd.NA

    phone = str(phone).strip()
    phone = re.sub(r"\D", "", phone)

    return phone


def validate_phone(phone):
    if pd.isna(phone) or str(phone).strip() == "":
        return "Missing"

    if len(str(phone)) == 11 and str(phone).startswith("01"):
        return "Valid"

    return "Invalid"


def standardize_date(date):
    if pd.isna(date) or str(date).strip() == "":
        return pd.NaT

    date = str(date).strip()

    if "/" in date:
        return pd.to_datetime(
            date,
            format="%d/%m/%Y",
            errors="coerce"
        )

    if "-" in date:
        return pd.to_datetime(
            date,
            format="%Y-%m-%d",
            errors="coerce"
        )

    return pd.NaT
