import pandas as pd
from pathlib import Path
from collections import defaultdict


# ============================================================
# PATHS
# ============================================================

BASE = Path(
    r"C:\Users\ann\Desktop\Y3S1\FIT3179\Visualization 2\Github Repo\DV2-FIT3179"
)

MASTER_FILE = (
    BASE
    / "data"
    / "clean"
    / "urban_wildlife_master.csv"
)

OUTPUT_FILE = (
    BASE
    / "data"
    / "final"
    / "10b_city_monthly_spiral.csv"
)


# ============================================================
# CONSTANTS
# ============================================================

CITIES = [
    "Sydney",
    "Melbourne",
    "Brisbane",
    "Adelaide",
    "Perth",
    "Hobart",
    "Darwin",
    "Canberra–Queanbeyan"
]

GROUPS = [
    "Bird",
    "Mammal",
    "Reptile",
    "Insect"
]

YEARS = list(range(2016, 2026))

MONTHS = list(range(1, 13))

MONTH_NAMES = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec"
}

CHUNK_SIZE = 250_000


# ============================================================
# AGGREGATORS
# ============================================================

record_parts = []

# Sets are required for exact distinct-species counting
# across multiple chunks.
richness_sets = defaultdict(set)

recovered_from_eventdate = 0
unrecoverable = 0
total_processed = 0


print("Processing city-level monthly wildlife data...\n")


# ============================================================
# READ MASTER IN CHUNKS
# ============================================================

for chunk_no, chunk in enumerate(

    pd.read_csv(
        MASTER_FILE,
        usecols=[
            "CITY",
            "year",
            "month",
            "eventDate",
            "species",
            "animal_group"
        ],
        chunksize=CHUNK_SIZE,
        low_memory=False
    ),

    start=1
):

    total_processed += len(chunk)


    # ========================================================
    # CLEAN YEAR
    # ========================================================

    chunk["year"] = pd.to_numeric(
        chunk["year"],
        errors="coerce"
    )


    # ========================================================
    # CLEAN ORIGINAL MONTH
    # ========================================================

    chunk["month_original"] = pd.to_numeric(
        chunk["month"],
        errors="coerce"
    )


    # ========================================================
    # RECOVER MISSING MONTH FROM eventDate
    # ========================================================

    parsed_event_date = pd.to_datetime(
        chunk["eventDate"],
        errors="coerce",
        utc=True
    )

    chunk["month_from_eventdate"] = (
        parsed_event_date.dt.month
    )


    original_valid = (
        chunk["month_original"]
        .between(1, 12)
    )

    eventdate_valid = (
        chunk["month_from_eventdate"]
        .between(1, 12)
    )


    # Use original month if valid.
    # Otherwise use month recovered from eventDate.
    chunk["month_final"] = (
        chunk["month_original"]
        .where(
            original_valid,
            chunk["month_from_eventdate"]
        )
    )


    # ========================================================
    # AUDIT RECOVERY
    # ========================================================

    recovered = (
        ~original_valid
        &
        eventdate_valid
    )

    failed = (
        ~original_valid
        &
        ~eventdate_valid
    )

    recovered_from_eventdate += recovered.sum()
    unrecoverable += failed.sum()


    # ========================================================
    # KEEP VALID STUDY RECORDS
    # ========================================================

    chunk = chunk[
        chunk["year"].between(2016, 2025)
        &
        chunk["month_final"].between(1, 12)
        &
        chunk["CITY"].isin(CITIES)
        &
        chunk["animal_group"].isin(GROUPS)
    ].copy()


    chunk["month_final"] = (
        chunk["month_final"]
        .astype(int)
    )


    # ========================================================
    # RECORD COUNTS
    # ========================================================

    records = (
        chunk
        .groupby(
            [
                "CITY",
                "year",
                "month_final",
                "animal_group"
            ]
        )
        .size()
        .reset_index(
            name="record_count"
        )
    )

    record_parts.append(records)


    # ========================================================
    # EXACT SPECIES RICHNESS
    # ========================================================

    species_rows = chunk[
        chunk["species"].notna()
    ]


    for key, values in species_rows.groupby(
        [
            "CITY",
            "year",
            "month_final",
            "animal_group"
        ]
    )["species"]:

        richness_sets[key].update(
            values.unique()
        )


    print(
        f"Chunk {chunk_no}: "
        f"{total_processed:,} rows processed"
    )


# ============================================================
# COMBINE RECORD COUNTS
# ============================================================

records = pd.concat(
    record_parts,
    ignore_index=True
)


records = (
    records
    .groupby(
        [
            "CITY",
            "year",
            "month_final",
            "animal_group"
        ],
        as_index=False
    )["record_count"]
    .sum()
)


records = records.rename(
    columns={
        "month_final": "month"
    }
)


# ============================================================
# BUILD SPECIES-RICHNESS TABLE
# ============================================================

richness_rows = []


for (
    city,
    year,
    month,
    group
), species_set in richness_sets.items():

    richness_rows.append({

        "CITY": city,

        "year": int(year),

        "month": int(month),

        "animal_group": group,

        "species_richness": len(species_set)
    })


richness = pd.DataFrame(
    richness_rows
)


# ============================================================
# CREATE COMPLETE 3,840-ROW GRID
# ============================================================

full_grid = pd.MultiIndex.from_product(

    [
        CITIES,
        YEARS,
        MONTHS,
        GROUPS
    ],

    names=[
        "CITY",
        "year",
        "month",
        "animal_group"
    ]

).to_frame(
    index=False
)


monthly = (
    full_grid
    .merge(
        records,
        on=[
            "CITY",
            "year",
            "month",
            "animal_group"
        ],
        how="left"
    )
    .merge(
        richness,
        on=[
            "CITY",
            "year",
            "month",
            "animal_group"
        ],
        how="left"
    )
)


# If a particular combination has no observations,
# keep the row and assign zero.
monthly["record_count"] = (
    monthly["record_count"]
    .fillna(0)
    .astype(int)
)

monthly["species_richness"] = (
    monthly["species_richness"]
    .fillna(0)
    .astype(int)
)


# ============================================================
# MONTH LABEL
# ============================================================

monthly["month_name"] = (
    monthly["month"]
    .map(MONTH_NAMES)
)


# ============================================================
# MONTH INDEX
#
# Jan 2016 = 0
# ...
# Dec 2025 = 119
# ============================================================

monthly["month_index"] = (

    (monthly["year"] - 2016) * 12

    +

    (monthly["month"] - 1)
)


# ============================================================
# DATE
# ============================================================

monthly["date"] = pd.to_datetime(
    dict(
        year=monthly["year"],
        month=monthly["month"],
        day=1
    )
)


monthly["date"] = (
    monthly["date"]
    .dt.strftime("%Y-%m-%d")
)


# ============================================================
# ANNUAL RECORD COUNT
#
# IMPORTANT:
# denominator is:
# CITY × YEAR × ANIMAL GROUP
# ============================================================

monthly["annual_record_count"] = (

    monthly
    .groupby(
        [
            "CITY",
            "year",
            "animal_group"
        ]
    )["record_count"]
    .transform("sum")
)


# ============================================================
# WITHIN-YEAR SHARE
# ============================================================

monthly["within_year_share"] = (

    monthly["record_count"]

    /

    monthly["annual_record_count"]
)


# Avoid problems if an entire city/year/group somehow has zero records.
monthly["within_year_share"] = (
    monthly["within_year_share"]
    .fillna(0)
)


monthly["within_year_pct"] = (

    monthly["within_year_share"]

    * 100

).round(3)


# ============================================================
# SORT
# ============================================================

city_order = {
    city: index
    for index, city in enumerate(CITIES)
}

group_order = {
    group: index
    for index, group in enumerate(GROUPS)
}


monthly["_city_order"] = (
    monthly["CITY"]
    .map(city_order)
)

monthly["_group_order"] = (
    monthly["animal_group"]
    .map(group_order)
)


monthly = (
    monthly
    .sort_values(
        [
            "_city_order",
            "_group_order",
            "month_index"
        ]
    )
    .drop(
        columns=[
            "_city_order",
            "_group_order"
        ]
    )
)


# ============================================================
# FINAL COLUMN ORDER
# ============================================================

monthly = monthly[
    [
        "CITY",
        "year",
        "month",
        "month_name",
        "month_index",
        "date",
        "animal_group",
        "record_count",
        "species_richness",
        "annual_record_count",
        "within_year_share",
        "within_year_pct"
    ]
]


# ============================================================
# SAVE
# ============================================================

monthly.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# REPORT
# ============================================================

print("\n========================================")
print("CITY MONTHLY SPIRAL DATASET CREATED")
print("========================================")

print(
    "Rows:",
    f"{len(monthly):,}"
)

print(
    "Expected rows:",
    f"{8 * 10 * 12 * 4:,}"
)

print(
    "Recovered from eventDate:",
    f"{recovered_from_eventdate:,}"
)

print(
    "Unrecoverable:",
    f"{unrecoverable:,}"
)

print(
    "Records represented:",
    f"{monthly['record_count'].sum():,}"
)

print(
    "\nRows per city:"
)

print(
    monthly["CITY"]
    .value_counts()
)

print(
    "\nRows per animal group:"
)

print(
    monthly["animal_group"]
    .value_counts()
)

print(
    "\nSaved to:"
)

print(
    OUTPUT_FILE
)