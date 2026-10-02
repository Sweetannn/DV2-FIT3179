import pandas as pd
from pathlib import Path
from collections import defaultdict
import h3


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

THREAT_FILE = (
    BASE
    / "data"
    / "final"
    / "09b_threatened_species_matches.csv"
)

OUTPUT_FILE = (
    BASE
    / "data"
    / "final"
    / "09c_threatened_occurrences.csv"
)


# ============================================================
# SETTINGS
# ============================================================

H3_RESOLUTION = 7

CHUNK_SIZE = 250_000

VALID_STATUSES = {
    "Critically Endangered",
    "Endangered",
    "Vulnerable"
}


# ============================================================
# H3 COMPATIBILITY HELPERS
# ============================================================

def latlng_to_cell(lat, lon, resolution):

    if hasattr(h3, "latlng_to_cell"):
        return h3.latlng_to_cell(
            lat,
            lon,
            resolution
        )

    return h3.geo_to_h3(
        lat,
        lon,
        resolution
    )


def cell_to_latlng(cell):

    if hasattr(h3, "cell_to_latlng"):
        return h3.cell_to_latlng(cell)

    return h3.h3_to_geo(cell)


# ============================================================
# LOAD THREATENED MATCH TABLE
# ============================================================

threat = pd.read_csv(
    THREAT_FILE,
    low_memory=False
)


print("Threat file columns:")
print(threat.columns.tolist())


# ============================================================
# DETECT STATUS COLUMN
# ============================================================

status_candidates = [
    "epbc_status",
    "status",
    "threatened_status",
    "threat_status"
]

status_col = None

for candidate in status_candidates:

    if candidate in threat.columns:
        status_col = candidate
        break


if status_col is None:

    raise ValueError(
        "Could not identify threatened status column "
        "in 09b_threatened_species_matches.csv"
    )


# ============================================================
# CHECK SPECIES COLUMN
# ============================================================

if "species" not in threat.columns:

    raise ValueError(
        "Expected a 'species' column in "
        "09b_threatened_species_matches.csv"
    )


# ============================================================
# KEEP ONLY MAIN THREATENED DEFINITION
# ============================================================

threat = threat[
    threat[status_col].isin(
        VALID_STATUSES
    )
].copy()


# ============================================================
# CREATE CANONICAL COMMON NAME
# ============================================================

def choose_common_name(row):

    epbc_name = row.get("epbc_common_name")

    if pd.notna(epbc_name):
        epbc_name = str(epbc_name).strip()

        if epbc_name:
            return epbc_name


    common_name = row.get("common_name")

    if pd.notna(common_name):
        common_name = str(common_name).strip()

        if common_name:
            return common_name


    return ""


threat["display_common_name"] = (
    threat.apply(
        choose_common_name,
        axis=1
    )
)


# ============================================================
# REMOVE DUPLICATE SPECIES MAPPINGS
# ============================================================

threat_unique = (
    threat[
        [
            "species",
            status_col,
            "display_common_name"
        ]
    ]
    .drop_duplicates(
        subset=[
            "species",
            status_col
        ]
    )
)


# ============================================================
# LOOKUPS
# ============================================================

status_lookup = dict(
    zip(
        threat_unique["species"],
        threat_unique[status_col]
    )
)


common_name_lookup = dict(
    zip(
        threat_unique["species"],
        threat_unique["display_common_name"]
    )
)


threatened_species = set(
    status_lookup.keys()
)


print(
    "\nThreatened species used:",
    len(threatened_species)
)


# ============================================================
# STORAGE
# ============================================================

# Key:
# CITY
# species
# animal_group
# status
# H3 cell
#
# NOTE:
# vernacularName is NOT included in the aggregation key.

counts = defaultdict(int)


matched_records = 0
valid_coordinate_records = 0


# ============================================================
# PROCESS MASTER FILE
# ============================================================

print(
    "\nProcessing master occurrence records...\n"
)


for chunk_no, chunk in enumerate(

    pd.read_csv(
        MASTER_FILE,
        usecols=[
            "CITY",
            "species",
            "animal_group",
            "decimalLatitude",
            "decimalLongitude"
        ],
        chunksize=CHUNK_SIZE,
        low_memory=False
    ),

    start=1
):

    # --------------------------------------------------------
    # KEEP ONLY THREATENED SPECIES
    # --------------------------------------------------------

    chunk = chunk[
        chunk["species"].isin(
            threatened_species
        )
    ].copy()


    matched_records += len(chunk)


    if len(chunk) == 0:

        print(
            f"Chunk {chunk_no}: no threatened records"
        )

        continue


    # --------------------------------------------------------
    # CLEAN COORDINATES
    # --------------------------------------------------------

    chunk["decimalLatitude"] = pd.to_numeric(
        chunk["decimalLatitude"],
        errors="coerce"
    )

    chunk["decimalLongitude"] = pd.to_numeric(
        chunk["decimalLongitude"],
        errors="coerce"
    )


    chunk = chunk[
        chunk["decimalLatitude"].between(
            -90,
            90
        )
        &
        chunk["decimalLongitude"].between(
            -180,
            180
        )
    ].copy()


    valid_coordinate_records += len(chunk)


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    chunk["status"] = (
        chunk["species"]
        .map(
            status_lookup
        )
    )


    # --------------------------------------------------------
    # H3 R7
    # --------------------------------------------------------

    chunk["h3_cell"] = [

        latlng_to_cell(
            lat,
            lon,
            H3_RESOLUTION
        )

        for lat, lon in zip(
            chunk["decimalLatitude"],
            chunk["decimalLongitude"]
        )
    ]


    # --------------------------------------------------------
    # AGGREGATE
    # --------------------------------------------------------

    grouped = (
        chunk
        .groupby(
            [
                "CITY",
                "species",
                "animal_group",
                "status",
                "h3_cell"
            ]
        )
        .size()
    )


    for key, value in grouped.items():

        counts[key] += int(value)


    print(
        f"Chunk {chunk_no}: "
        f"{matched_records:,} threatened records encountered"
    )


# ============================================================
# BUILD FINAL OUTPUT
# ============================================================

rows = []


for (
    city,
    species,
    animal_group,
    status,
    h3_cell
), record_count in counts.items():

    latitude, longitude = (
        cell_to_latlng(
            h3_cell
        )
    )


    rows.append({

        "CITY":
            city,

        "scientificName":
            species,

        "vernacularName":
            common_name_lookup.get(
                species,
                ""
            ),

        "animal_group":
            animal_group,

        "status":
            status,

        "h3_cell":
            h3_cell,

        "latitude":
            round(
                float(latitude),
                6
            ),

        "longitude":
            round(
                float(longitude),
                6
            ),

        "record_count":
            record_count
    })


result = pd.DataFrame(
    rows
)


# ============================================================
# SORT
# ============================================================

status_order = {
    "Critically Endangered": 1,
    "Endangered": 2,
    "Vulnerable": 3
}


result["_status_order"] = (
    result["status"]
    .map(
        status_order
    )
)


result = (
    result
    .sort_values(
        [
            "_status_order",
            "CITY",
            "scientificName",
            "h3_cell"
        ]
    )
    .drop(
        columns=[
            "_status_order"
        ]
    )
)


# ============================================================
# SAVE
# ============================================================

result.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# REPORT
# ============================================================

print(
    "\n========================================"
)

print(
    "THREATENED OCCURRENCE DATASET CREATED"
)

print(
    "========================================"
)


print(
    "Threatened master records:",
    f"{matched_records:,}"
)

print(
    "Valid-coordinate records:",
    f"{valid_coordinate_records:,}"
)

print(
    "Aggregated output rows:",
    f"{len(result):,}"
)

print(
    "Aggregated record total:",
    f"{result['record_count'].sum():,}"
)


print(
    "\nDistinct threatened species:"
)

print(
    result["scientificName"]
    .nunique()
)


print(
    "\nDistinct species by status:"
)

print(
    result.groupby(
        "status"
    )["scientificName"]
    .nunique()
)


print(
    "\nRows by threat status:"
)

print(
    result["status"]
    .value_counts()
)


print(
    "\nSaved to:"
)

print(
    OUTPUT_FILE
)