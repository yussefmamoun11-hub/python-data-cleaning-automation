import os
import sys
import logging
import pandas as pd

from cleaner import clean_dataset
from reporter import generate_quality_report


DEFAULT_INPUT = "data/input/customers_january.csv"
OUTPUT_DIR = "data/output"
REPORT_DIR = "reports"
LOG_DIR = "logs"


def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)

    logging.basicConfig(
        filename="logs/pipeline.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def main():
    setup_logging()

    input_file = (
        sys.argv[1]
        if len(sys.argv) > 1
        else DEFAULT_INPUT
    )

    if not os.path.exists(input_file):
        print(f"ERROR: Input file not found: {input_file}")
        logging.error(
            "Input file not found: %s",
            input_file
        )
        sys.exit(1)

    try:
        logging.info(
            "Starting pipeline for: %s",
            input_file
        )

        if input_file.lower().endswith(".xlsx"):
            original_df = pd.read_excel(input_file)
        else:
            original_df = pd.read_csv(input_file)

        original_rows = len(original_df)

        df = clean_dataset(input_file)

        os.makedirs(
            OUTPUT_DIR,
            exist_ok=True
        )

        os.makedirs(
            REPORT_DIR,
            exist_ok=True
        )

        base_name = os.path.splitext(
            os.path.basename(input_file)
        )[0]

        output_file = os.path.join(
            OUTPUT_DIR,
            f"cleaned_{base_name}.csv"
        )

        report_file = os.path.join(
            REPORT_DIR,
            f"{base_name}_quality_report.txt"
        )

        df.to_csv(
            output_file,
            index=False
        )

        generate_quality_report(
            input_file,
            df,
            report_file
        )

        logging.info(
            "Pipeline completed successfully"
        )

        print("=== DATA CLEANING PIPELINE ===")
        print()
        print("Input file:", input_file)
        print("Original rows:", original_rows)
        print("Final rows:", len(df))
        print("Output file:", output_file)
        print("Report file:", report_file)
        print()
        print("=== PIPELINE COMPLETED ===")

    except Exception as error:
        logging.exception(
            "Pipeline failed"
        )

        print()
        print("ERROR:", error)
        sys.exit(1)


if __name__ == "__main__":
    main()
