import pandas as pd
from pathlib import Path


# ============================================================
# PATH
# ============================================================

BASE = Path(
    r"C:\Users\ann\Desktop\Y3S1\FIT3179\Visualization 2\Github Repo\DV2-FIT3179"
)

FILE = (
    BASE
    / "data"
    / "final"
    / "09c_threatened_occurrences.csv"
)


# ============================================================
# LOAD
# ============================================================

df = pd.read_csv(
    FILE
)


# ============================================================
# BASIC
# ============================================================

print("\n================================")
print("BASIC")
print("================================")

print(
    "Rows:",
    f"{len(df):,}"
)

print(
    "Columns:",
    df.columns.tolist()
)


# ============================================================
# STATUS
# ============================================================

print("\n================================")
print("ROWS BY STATUS")
print("================================")

print(
    df["status"]
    .value_counts()
)


# ============================================================
# DISTINCT SPECIES
# ============================================================

print("\n================================")
print("DISTINCT SPECIES")
print("================================")

print(
    "Total:",
    df["scientificName"]
    .nunique()
)


print(
    "\nBy status:"
)

species_by_status = (
    df.groupby(
        "status"
    )["scientificName"]
    .nunique()
)

print(
    species_by_status
)


# ============================================================
# CHECK EXPECTED STATUS SPECIES TOTALS
# ============================================================

expected_species_status = {
    "Critically Endangered": 17,
    "Endangered": 40,
    "Vulnerable": 53
}


print("\n================================")
print("STATUS SPECIES CHECK")
print("================================")

for status, expected in expected_species_status.items():

    actual = int(
        species_by_status.get(
            status,
            0
        )
    )

    print(
        f"{status}: "
        f"{actual} "
        f"(expected {expected}) "
        f"-> {actual == expected}"
    )


# ============================================================
# ANIMAL GROUP
# ============================================================

print("\n================================")
print("ROWS BY ANIMAL GROUP")
print("================================")

print(
    df["animal_group"]
    .value_counts()
)


print(
    "\nDistinct species by animal group:"
)

print(
    df.groupby(
        "animal_group"
    )["scientificName"]
    .nunique()
)


# ============================================================
# CITY
# ============================================================

print("\n================================")
print("ROWS BY CITY")
print("================================")

print(
    df["CITY"]
    .value_counts()
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
# DUPLICATE KEY CHECK
# ============================================================

duplicate_keys = (
    df[
        [
            "CITY",
            "scientificName",
            "status",
            "h3_cell"
        ]
    ]
    .duplicated()
    .sum()
)


print("\n================================")
print("DUPLICATE KEYS")
print("================================")

print(
    duplicate_keys
)


# ============================================================
# COMMON NAME CONSISTENCY
# ============================================================

name_count = (
    df.groupby(
        "scientificName"
    )["vernacularName"]
    .nunique(
        dropna=False
    )
)


multiple_names = (
    name_count[
        name_count > 1
    ]
)


print("\n================================")
print("COMMON NAME CONSISTENCY")
print("================================")

print(
    "Species with multiple display common names:",
    len(multiple_names)
)


if len(multiple_names) > 0:

    print(
        multiple_names
    )


# ============================================================
# COORDINATE RANGE
# ============================================================

print("\n================================")
print("COORDINATE RANGE")
print("================================")

print(
    "Latitude:",
    df["latitude"].min(),
    "to",
    df["latitude"].max()
)

print(
    "Longitude:",
    df["longitude"].min(),
    "to",
    df["longitude"].max()
)


# ============================================================
# STATUS VALIDITY
# ============================================================

allowed_statuses = {
    "Critically Endangered",
    "Endangered",
    "Vulnerable"
}


invalid_statuses = set(
    df["status"]
    .dropna()
    .unique()
) - allowed_statuses


print("\n================================")
print("INVALID STATUSES")
print("================================")

print(
    invalid_statuses
)


# ============================================================
# SAMPLE
# ============================================================

print("\n================================")
print("SAMPLE")
print("================================")

print(
    df.head(20)
    .to_string(
        index=False
    )
)