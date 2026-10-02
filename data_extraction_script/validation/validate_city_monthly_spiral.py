import pandas as pd
from pathlib import Path


BASE = Path(
    r"C:\Users\ann\Desktop\Y3S1\FIT3179\Visualization 2\Github Repo\DV2-FIT3179"
)

FILE = (
    BASE
    / "data"
    / "final"
    / "10b_city_monthly_spiral.csv"
)


df = pd.read_csv(FILE)


print("\n================================")
print("BASIC CHECK")
print("================================")

print(
    "Rows:",
    len(df)
)

print(
    "Expected:",
    8 * 10 * 12 * 4
)

print(
    "Columns:",
    len(df.columns)
)


# ============================================================
# CITY CHECK
# ============================================================

print("\n================================")
print("ROWS PER CITY")
print("================================")

print(
    df["CITY"]
    .value_counts()
)


# ============================================================
# GROUP CHECK
# ============================================================

print("\n================================")
print("ROWS PER ANIMAL GROUP")
print("================================")

print(
    df["animal_group"]
    .value_counts()
)


# ============================================================
# YEAR CHECK
# ============================================================

print("\n================================")
print("ROWS PER YEAR")
print("================================")

print(
    df["year"]
    .value_counts()
    .sort_index()
)


# ============================================================
# DUPLICATES
# ============================================================

duplicates = (
    df[
        [
            "CITY",
            "year",
            "month",
            "animal_group"
        ]
    ]
    .duplicated()
    .sum()
)


print("\n================================")
print("DUPLICATE COMBINATIONS")
print("================================")

print(
    duplicates
)


# ============================================================
# MONTH INDEX
# ============================================================

print("\n================================")
print("MONTH INDEX")
print("================================")

print(
    df["month_index"].min(),
    "to",
    df["month_index"].max()
)


# ============================================================
# NORMALISATION CHECK
# ============================================================

share_check = (

    df.groupby(
        [
            "CITY",
            "year",
            "animal_group"
        ]
    )["within_year_share"]
    .sum()
)


print("\n================================")
print("WITHIN-YEAR SHARE CHECK")
print("================================")

print(
    "Minimum:",
    share_check.min()
)

print(
    "Maximum:",
    share_check.max()
)


bad_shares = share_check[
    ~share_check.between(
        0.999999,
        1.000001
    )
]


print(
    "Groups not summing to ~1:",
    len(bad_shares)
)


if len(bad_shares) > 0:

    print(
        bad_shares
    )


# ============================================================
# RECORD TOTAL
# ============================================================

print("\n================================")
print("RECORD TOTAL")
print("================================")

print(
    f"{df['record_count'].sum():,}"
)


# ============================================================
# ZERO ANNUAL TOTALS
# ============================================================

zero_annual = df[
    df["annual_record_count"] == 0
][
    [
        "CITY",
        "year",
        "animal_group"
    ]
].drop_duplicates()


print("\n================================")
print("ZERO ANNUAL TOTALS")
print("================================")

print(
    len(zero_annual)
)


if len(zero_annual) > 0:

    print(
        zero_annual.to_string(
            index=False
        )
    )


# ============================================================
# SPECIES RICHNESS CHECK
# ============================================================

print("\n================================")
print("RICHNESS RANGE")
print("================================")

print(
    "Minimum:",
    df["species_richness"].min()
)

print(
    "Maximum:",
    df["species_richness"].max()
)


# ============================================================
# SAMPLE
# ============================================================

print("\n================================")
print("SAMPLE")
print("================================")

print(
    df.head(20).to_string(
        index=False
    )
)