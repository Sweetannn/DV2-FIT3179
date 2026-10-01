import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE = Path(
    r"C:\Users\ann\Desktop\Y3S1\FIT3179\Visualization 2\Github Repo\DV2-FIT3179"
)

SPECIES_FILE = (
    BASE
    / "data"
    / "final"
    / "05_species_city_coverage.csv"
)

EPBC_FILE = (
    BASE
    / "data"
    / "clean"
    / "epbc_current_threatened_fauna_for_join.csv"
)

OUTPUT_DIR = (
    BASE
    / "data"
    / "final"
)

CITY_OUTPUT = (
    OUTPUT_DIR
    / "09_threatened_city_summary.csv"
)

MATCH_OUTPUT = (
    OUTPUT_DIR
    / "09b_threatened_species_matches.csv"
)


# ============================================================
# CITIES
# ============================================================

CITIES = [
    "Sydney",
    "Melbourne",
    "Brisbane",
    "Adelaide",
    "Perth",
    "Hobart",
    "Darwin",
    "Canberra–Queanbeyan",
]


# ============================================================
# LOAD DATA
# ============================================================

species = pd.read_csv(
    SPECIES_FILE,
    low_memory=False
)

epbc = pd.read_csv(
    EPBC_FILE,
    low_memory=False
)


print("ALA species:", len(species))
print("EPBC current listings:", len(epbc))


# ============================================================
# CLEAN SCIENTIFIC NAMES
# ============================================================

def clean_name(series):
    return (
        series
        .fillna("")
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.lower()
    )


species["species_clean"] = clean_name(
    species["species"]
)

epbc["match_name_clean"] = clean_name(
    epbc["match_name_primary"]
)

epbc["accepted_name_clean"] = clean_name(
    epbc["accepted_scientific_name"]
)

epbc["listed_name_clean"] = clean_name(
    epbc["epbc_listed_name"]
)


# ============================================================
# KEEP CURRENT, NON-SCOPED LISTINGS
# ============================================================
#
# Scoped listings may refer to only a population/subspecies.
# We do not automatically classify the whole species as
# threatened from a species-level ALA record.
# ============================================================

epbc["is_current_threatened"] = (
    epbc["is_current_threatened"]
    .astype(str)
    .str.upper()
    .eq("TRUE")
)

epbc["is_scoped_listing"] = (
    epbc["is_scoped_listing"]
    .astype(str)
    .str.upper()
    .eq("TRUE")
)

epbc_use = epbc[
    (epbc["is_current_threatened"])
    &
    (~epbc["is_scoped_listing"])
].copy()


print(
    "Current non-scoped EPBC listings:",
    len(epbc_use)
)


# ============================================================
# BUILD LOOKUP OF ALL USEFUL EPBC SCIENTIFIC NAMES
# ============================================================

lookup_rows = []

for _, row in epbc_use.iterrows():

    candidate_names = {
        row["match_name_clean"],
        row["accepted_name_clean"],
        row["listed_name_clean"],
    }

    candidate_names.discard("")

    for name in candidate_names:

        lookup_rows.append({
            "join_name": name,
            "epbc_status": row["epbc_status"],
            "epbc_listed_name": row["epbc_listed_name"],
            "accepted_scientific_name":
                row["accepted_scientific_name"],
            "epbc_common_name":
                row["common_name"],
            "effective_date":
                row["effective_date"]
        })


lookup = pd.DataFrame(lookup_rows)

# Remove duplicate name mappings
lookup = lookup.drop_duplicates(
    subset=[
        "join_name",
        "epbc_status",
        "epbc_listed_name"
    ]
)


# ============================================================
# MATCH ALA SPECIES TO EPBC
# ============================================================

matched = species.merge(
    lookup,
    left_on="species_clean",
    right_on="join_name",
    how="left"
)

matched["is_threatened"] = (
    matched["epbc_status"].notna()
)


# ============================================================
# DEAL WITH POSSIBLE MULTIPLE EPBC MATCHES
# ============================================================
#
# If one ALA species matched more than one EPBC row,
# keep one row using the most severe category.
# ============================================================

status_order = {
    "Critically Endangered": 1,
    "Endangered": 2,
    "Vulnerable": 3,
    "Conservation Dependent": 4,
}

matched["status_rank"] = (
    matched["epbc_status"]
    .map(status_order)
    .fillna(99)
)

matched = (
    matched
    .sort_values(
        [
            "species",
            "status_rank"
        ]
    )
    .drop_duplicates(
        subset=["species"],
        keep="first"
    )
)


# ============================================================
# SAVE SPECIES-LEVEL MATCH FILE
# ============================================================

match_columns = [
    "species",
    "common_name",
    "animal_group",
    "cities_present",
    "city_list",
    "record_count",
    "is_threatened",
    "epbc_status",
    "epbc_listed_name",
    "accepted_scientific_name",
    "epbc_common_name",
    "effective_date",
]

matched[
    match_columns
].to_csv(
    MATCH_OUTPUT,
    index=False
)


# ============================================================
# CITY SUMMARY
# ============================================================

city_rows = []


for city in CITIES:

    # Species recorded in this city
    city_species = matched[
        matched["city_list"]
        .fillna("")
        .str.split(" | ", regex=False)
        .apply(lambda x: city in x)
    ].copy()

    total_species = len(
        city_species
    )

    threatened = city_species[
        city_species["is_threatened"]
    ]

    threatened_species = len(
        threatened
    )

    threatened_share = (
        threatened_species
        / total_species
        * 100
        if total_species > 0
        else 0
    )

    # Category counts
    critically_endangered = (
        threatened[
            "epbc_status"
        ]
        .eq("Critically Endangered")
        .sum()
    )

    endangered = (
        threatened[
            "epbc_status"
        ]
        .eq("Endangered")
        .sum()
    )

    vulnerable = (
        threatened[
            "epbc_status"
        ]
        .eq("Vulnerable")
        .sum()
    )

    conservation_dependent = (
        threatened[
            "epbc_status"
        ]
        .eq("Conservation Dependent")
        .sum()
    )

    city_rows.append({

        "city":
            city,

        "recorded_species":
            total_species,

        "threatened_species":
            threatened_species,

        "threatened_share_pct":
            round(
                threatened_share,
                3
            ),

        "critically_endangered":
            critically_endangered,

        "endangered":
            endangered,

        "vulnerable":
            vulnerable,

        "conservation_dependent":
            conservation_dependent
    })


city_summary = pd.DataFrame(
    city_rows
)


city_summary.to_csv(
    CITY_OUTPUT,
    index=False
)


# ============================================================
# PRINT RESULTS
# ============================================================

print("\n===================================")
print("THREATENED SPECIES MATCHING")
print("===================================")

print(
    "ALA species:",
    len(matched)
)

print(
    "Matched threatened species:",
    matched["is_threatened"].sum()
)

print(
    "Unmatched/not threatened:",
    (~matched["is_threatened"]).sum()
)


print("\n===================================")
print("CITY SUMMARY")
print("===================================")

print(
    city_summary.to_string(
        index=False
    )
)

print("\nSaved:")
print(CITY_OUTPUT)
print(MATCH_OUTPUT)