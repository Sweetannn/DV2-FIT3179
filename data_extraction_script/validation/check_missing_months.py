import pandas as pd
from pathlib import Path
from collections import Counter


BASE = Path(
    r"C:\Users\ann\Desktop\Y3S1\FIT3179\Visualization 2\Github Repo\DV2-FIT3179"
)

MASTER_FILE = (
    BASE
    / "data"
    / "clean"
    / "urban_wildlife_master.csv"
)


CHUNK_SIZE = 250_000


total_rows = 0
valid_month_rows = 0
missing_month_rows = 0
invalid_month_rows = 0

recoverable_from_eventdate = 0
unrecoverable = 0


missing_by_group = Counter()
missing_by_year = Counter()
missing_by_city = Counter()


examples = []


for chunk in pd.read_csv(
    MASTER_FILE,
    usecols=[
        "year",
        "month",
        "eventDate",
        "animal_group",
        "CITY",
        "species"
    ],
    chunksize=CHUNK_SIZE,
    low_memory=False
):

    total_rows += len(chunk)

    # -----------------------------------------
    # Convert month to numeric
    # -----------------------------------------

    month_numeric = pd.to_numeric(
        chunk["month"],
        errors="coerce"
    )

    valid_month = (
        month_numeric.between(1, 12)
    )

    missing_month = (
        month_numeric.isna()
    )

    invalid_month = (
        month_numeric.notna()
        &
        ~month_numeric.between(1, 12)
    )


    valid_month_rows += valid_month.sum()
    missing_month_rows += missing_month.sum()
    invalid_month_rows += invalid_month.sum()


    # -----------------------------------------
    # Rows without usable month
    # -----------------------------------------

    problem = chunk[
        ~valid_month
    ].copy()


    if len(problem) == 0:
        continue


    # -----------------------------------------
    # Group/year/city breakdown
    # -----------------------------------------

    missing_by_group.update(
        problem["animal_group"]
        .value_counts()
        .to_dict()
    )

    missing_by_year.update(
        problem["year"]
        .value_counts()
        .to_dict()
    )

    missing_by_city.update(
        problem["CITY"]
        .value_counts()
        .to_dict()
    )


    # -----------------------------------------
    # Try parsing eventDate
    # -----------------------------------------

    parsed_date = pd.to_datetime(
        problem["eventDate"],
        errors="coerce",
        utc=True
    )

    parsed_month = parsed_date.dt.month

    recoverable = (
        parsed_month.between(1, 12)
    )

    recoverable_from_eventdate += (
        recoverable.sum()
    )

    unrecoverable += (
        (~recoverable).sum()
    )


    # -----------------------------------------
    # Save a few examples
    # -----------------------------------------

    if len(examples) < 20:

        sample = problem.head(
            20 - len(examples)
        )

        examples.extend(
            sample.to_dict(
                orient="records"
            )
        )


print("\n==============================")
print("MONTH AUDIT")
print("==============================")

print(
    "Total master rows:",
    f"{total_rows:,}"
)

print(
    "Valid month rows:",
    f"{valid_month_rows:,}"
)

print(
    "Missing month rows:",
    f"{missing_month_rows:,}"
)

print(
    "Invalid month rows:",
    f"{invalid_month_rows:,}"
)

print(
    "Total without usable month:",
    f"{missing_month_rows + invalid_month_rows:,}"
)


print("\nRecoverable from eventDate:")

print(
    f"{recoverable_from_eventdate:,}"
)


print("\nStill unrecoverable:")

print(
    f"{unrecoverable:,}"
)


print("\n=== BY ANIMAL GROUP ===")

for key, value in (
    missing_by_group.most_common()
):
    print(
        key,
        f"{value:,}"
    )


print("\n=== BY YEAR ===")

for key in sorted(
    missing_by_year
):
    print(
        key,
        f"{missing_by_year[key]:,}"
    )


print("\n=== BY CITY ===")

for key, value in (
    missing_by_city.most_common()
):
    print(
        key,
        f"{value:,}"
    )


print("\n=== EXAMPLES ===")

for row in examples:
    print(row)