from pathlib import Path
import pandas as pd


# =========================================================
# CONFIGURATION
# =========================================================

INPUT = Path("data/final/04_city_year_richness.csv")

EXPECTED_YEARS = list(range(2016, 2026))

EXPECTED_CITIES = [
    "Brisbane",
    "Sydney",
    "Melbourne",
    "Canberra–Queanbeyan",
    "Adelaide",
    "Perth",
    "Hobart",
    "Darwin",
]


# =========================================================
# LOAD DATA
# =========================================================

if not INPUT.exists():
    raise FileNotFoundError(
        f"Cannot find: {INPUT}"
    )

df = pd.read_csv(INPUT)


# =========================================================
# REQUIRED COLUMNS
# =========================================================

required = {
    "year",
    "city",
    "species_richness",
    "record_count",
}

missing = required - set(df.columns)

if missing:
    raise ValueError(
        f"Missing required columns: {sorted(missing)}"
    )


# =========================================================
# CLEAN TYPES
# =========================================================

df["year"] = pd.to_numeric(
    df["year"],
    errors="raise"
).astype(int)

df["species_richness"] = pd.to_numeric(
    df["species_richness"],
    errors="raise"
).astype(int)

df["record_count"] = pd.to_numeric(
    df["record_count"],
    errors="raise"
).astype(int)

df["city"] = df["city"].astype(str).str.strip()


# =========================================================
# BASIC VALIDATION
# =========================================================

print("\n==============================")
print("BASIC")
print("==============================")

print("Rows:", len(df))
print("Expected rows:", 80)

if len(df) != 80:
    raise ValueError(
        f"Expected 80 rows but found {len(df)}."
    )


# =========================================================
# YEAR CHECK
# =========================================================

actual_years = sorted(df["year"].unique().tolist())

print("\n==============================")
print("YEARS")
print("==============================")

print("Actual:", actual_years)
print("Expected:", EXPECTED_YEARS)

if actual_years != EXPECTED_YEARS:
    raise ValueError(
        "Year range does not match 2016–2025."
    )


# =========================================================
# CITY CHECK
# =========================================================

actual_cities = sorted(df["city"].unique().tolist())
expected_cities = sorted(EXPECTED_CITIES)

print("\n==============================")
print("CITIES")
print("==============================")

print("Actual:")
print(actual_cities)

if actual_cities != expected_cities:
    raise ValueError(
        "City list does not match the expected eight cities."
    )


# =========================================================
# DUPLICATE CHECK
# =========================================================

duplicates = df.duplicated(
    subset=["year", "city"],
    keep=False
)

print("\n==============================")
print("DUPLICATES")
print("==============================")

print("Duplicate city-year rows:", duplicates.sum())

if duplicates.any():
    print(
        df.loc[
            duplicates,
            ["year", "city"]
        ].sort_values(
            ["year", "city"]
        )
    )

    raise ValueError(
        "Duplicate city-year combinations found."
    )


# =========================================================
# COMPLETE COVERAGE
# =========================================================

coverage = (
    df.groupby("city")["year"]
    .nunique()
    .sort_index()
)

print("\n==============================")
print("YEARS PER CITY")
print("==============================")

print(coverage)

if not (coverage == 10).all():
    raise ValueError(
        "Every city must contain all 10 years."
    )


# =========================================================
# NON-NEGATIVE VALUES
# =========================================================

if (df["species_richness"] < 0).any():
    raise ValueError(
        "Negative species richness found."
    )

if (df["record_count"] < 0).any():
    raise ValueError(
        "Negative record count found."
    )


# =========================================================
# COMPUTE DISPLAY RANK
#
# Rank primarily by annual recorded species richness.
# Record count breaks richness ties.
# City name provides deterministic final ordering.
# =========================================================

ranked = df.sort_values(
    by=[
        "year",
        "species_richness",
        "record_count",
        "city"
    ],
    ascending=[
        True,
        False,
        False,
        True
    ]
).copy()

ranked["rank"] = (
    ranked.groupby("year")
    .cumcount()
    + 1
)


# =========================================================
# CHECK RANKS
# =========================================================

expected_ranks = set(range(1, 9))

for year, group in ranked.groupby("year"):

    actual_ranks = set(
        group["rank"].tolist()
    )

    if actual_ranks != expected_ranks:
        raise ValueError(
            f"Invalid ranks for {year}: "
            f"{sorted(actual_ranks)}"
        )


# =========================================================
# SUMMARY
# =========================================================

print("\n==============================")
print("TOP CITY BY YEAR")
print("==============================")

print(
    ranked.loc[
        ranked["rank"] == 1,
        [
            "year",
            "city",
            "species_richness",
            "record_count"
        ]
    ].to_string(index=False)
)


print("\n==============================")
print("2016 VS 2025")
print("==============================")

comparison = ranked[
    ranked["year"].isin([2016, 2025])
][
    [
        "year",
        "city",
        "rank",
        "species_richness",
        "record_count"
    ]
].sort_values(
    ["year", "rank"]
)

print(
    comparison.to_string(index=False)
)


print("\n==============================")
print("VALIDATION PASSED")
print("==============================")