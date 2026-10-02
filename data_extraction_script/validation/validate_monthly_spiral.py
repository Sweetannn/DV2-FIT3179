import pandas as pd
from pathlib import Path


BASE = Path(
    r"C:\Users\ann\Desktop\Y3S1\FIT3179\Visualization 2\Github Repo\DV2-FIT3179"
)

FILE = (
    BASE
    / "data"
    / "final"
    / "10_monthly_spiral.csv"
)


df = pd.read_csv(
    FILE
)


print(
    "\n=== BASIC ==="
)

print(
    "Rows:",
    len(df)
)

print(
    "Columns:",
    len(df.columns)
)


print(
    "\n=== GROUP COUNTS ==="
)

print(
    df[
        "animal_group"
    ]
    .value_counts()
)


print(
    "\n=== YEARS ==="
)

print(
    df[
        "year"
    ]
    .value_counts()
    .sort_index()
)


print(
    "\n=== MONTH INDEX ==="
)

print(
    df[
        "month_index"
    ]
    .min(),
    "to",
    df[
        "month_index"
    ]
    .max()
)


print(
    "\n=== MISSING MONTHS ==="
)

print(
    df[
        [
            "year",
            "month",
            "animal_group"
        ]
    ]
    .duplicated()
    .sum()
)


print(
    "\n=== WITHIN-YEAR SHARE CHECK ==="
)

check = (
    df.groupby(
        [
            "year",
            "animal_group"
        ]
    )[
        "within_year_share"
    ]
    .sum()
)

print(
    check
)


print(
    "\nMinimum:",
    check.min()
)

print(
    "Maximum:",
    check.max()
)


print(
    "\n=== MONTHLY RECORD TOTAL ==="
)

print(
    df[
        "record_count"
    ].sum()
)