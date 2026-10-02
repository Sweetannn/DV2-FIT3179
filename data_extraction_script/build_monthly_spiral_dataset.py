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
    / "10_monthly_spiral.csv"
)


# ============================================================
# CONSTANTS
# ============================================================

YEARS = list(range(2016, 2026))

MONTHS = list(range(1, 13))

GROUPS = [
    "Bird",
    "Mammal",
    "Reptile",
    "Insect"
]

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

richness_sets = defaultdict(set)

recovered_from_eventdate = 0

unrecoverable = 0

total_processed = 0


print("Processing monthly wildlife data...\n")


# ============================================================
# READ MASTER
# ============================================================

for chunk_no, chunk in enumerate(

    pd.read_csv(
        MASTER_FILE,
        usecols=[
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


    # --------------------------------------------------------
    # CLEAN YEAR
    # --------------------------------------------------------

    chunk["year"] = pd.to_numeric(
        chunk["year"],
        errors="coerce"
    )


    # --------------------------------------------------------
    # CLEAN ORIGINAL MONTH
    # --------------------------------------------------------

    chunk["month_original"] = pd.to_numeric(
        chunk["month"],
        errors="coerce"
    )


    # --------------------------------------------------------
    # PARSE eventDate
    # --------------------------------------------------------

    parsed_event_date = pd.to_datetime(
        chunk["eventDate"],
        errors="coerce",
        utc=True
    )

    chunk["month_from_eventdate"] = (
        parsed_event_date.dt.month
    )


    # --------------------------------------------------------
    # BUILD FINAL MONTH
    #
    # Priority:
    # 1. Existing valid month
    # 2. eventDate-derived month
    # --------------------------------------------------------

    original_valid = (
        chunk["month_original"]
        .between(1, 12)
    )

    eventdate_valid = (
        chunk["month_from_eventdate"]
        .between(1, 12)
    )


    chunk["month_final"] = (
        chunk["month_original"]
        .where(
            original_valid,
            chunk["month_from_eventdate"]
        )
    )


    # --------------------------------------------------------
    # AUDIT RECOVERY
    # --------------------------------------------------------

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

    recovered_from_eventdate += (
        recovered.sum()
    )

    unrecoverable += (
        failed.sum()
    )


    # --------------------------------------------------------
    # KEEP VALID ANALYSIS ROWS
    # --------------------------------------------------------

    chunk = chunk[
        chunk["year"].between(
            2016,
            2025
        )
        &
        chunk["month_final"].between(
            1,
            12
        )
        &
        chunk["animal_group"].isin(
            GROUPS
        )
    ].copy()


    chunk["month_final"] = (
        chunk["month_final"]
        .astype(int)
    )


    # ========================================================
    # OCCURRENCE COUNTS
    # ========================================================

    records = (
        chunk
        .groupby(
            [
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

    record_parts.append(
        records
    )


    # ========================================================
    # EXACT SPECIES RICHNESS
    #
    # Use sets so species are not double-counted
    # across chunks.
    # ========================================================

    species_rows = chunk[
        chunk["species"].notna()
    ]


    for key, values in species_rows.groupby(
        [
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
        "month_final":
            "month"
    }
)


# ============================================================
# BUILD SPECIES RICHNESS TABLE
# ============================================================

richness_rows = []


for (
    year,
    month,
    group
), species_set in richness_sets.items():

    richness_rows.append({

        "year":
            int(year),

        "month":
            int(month),

        "animal_group":
            group,

        "species_richness":
            len(species_set)
    })


richness = pd.DataFrame(
    richness_rows
)


# ============================================================
# COMPLETE 480-ROW GRID
# ============================================================

full_grid = pd.MultiIndex.from_product(

    [
        YEARS,
        MONTHS,
        GROUPS
    ],

    names=[
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
            "year",
            "month",
            "animal_group"
        ],
        how="left"
    )
    .merge(
        richness,
        on=[
            "year",
            "month",
            "animal_group"
        ],
        how="left"
    )
)


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
# ADD TIME LABELS
# ============================================================

monthly["month_name"] = (
    monthly["month"]
    .map(MONTH_NAMES)
)


monthly["month_index"] = (

    (
        monthly["year"]
        - 2016
    )
    * 12

    +

    (
        monthly["month"]
        - 1
    )
)


monthly["date"] = pd.to_datetime(
    dict(
        year=
            monthly["year"],

        month=
            monthly["month"],

        day=
            1
    )
)


monthly["date"] = (
    monthly["date"]
    .dt.strftime(
        "%Y-%m-%d"
    )
)


# ============================================================
# NORMALISE WITHIN YEAR × GROUP
# ============================================================

monthly["annual_record_count"] = (

    monthly
    .groupby(
        [
            "year",
            "animal_group"
        ]
    )["record_count"]
    .transform("sum")
)


monthly["within_year_share"] = (

    monthly["record_count"]

    /

    monthly["annual_record_count"]
)


monthly["within_year_pct"] = (

    monthly["within_year_share"]

    * 100

).round(3)


# ============================================================
# SORT
# ============================================================

monthly = monthly.sort_values(
    [
        "animal_group",
        "month_index"
    ]
)


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

print("\n======================================")
print("MONTHLY SPIRAL DATASET CREATED")
print("======================================")

print(
    "Rows:",
    len(monthly)
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
    "Master rows:",
    f"{total_processed:,}"
)

print(
    "Excluded from monthly analysis:",
    f"{total_processed - monthly['record_count'].sum():,}"
)

print(
    "Month index:",
    monthly["month_index"].min(),
    "to",
    monthly["month_index"].max()
)

print(
    "\nSaved to:"
)

print(
    OUTPUT_FILE
)