import os
import pandas as pd


CLEANED_FILE = (
    "data/output/cleaned_customers_january.csv"
)


def test_output_file_exists():
    assert os.path.exists(
        CLEANED_FILE
    )


def test_final_row_count():
    df = pd.read_csv(CLEANED_FILE)

    assert len(df) == 9


def test_no_duplicate_customer_ids():
    df = pd.read_csv(CLEANED_FILE)

    assert (
        df["Customer ID"]
        .duplicated()
        .sum()
        == 0
    )


def test_city_has_no_missing_values():
    df = pd.read_csv(CLEANED_FILE)

    assert (
        df["City"]
        .isnull()
        .sum()
        == 0
    )


def test_email_validation():
    df = pd.read_csv(CLEANED_FILE)

    assert (
        df["Email Status"] == "Invalid"
    ).sum() == 2


def test_phone_validation():
    df = pd.read_csv(CLEANED_FILE)

    assert (
        df["Phone Status"] == "Invalid"
    ).sum() == 1
