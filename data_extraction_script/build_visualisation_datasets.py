import pandas as pd
import json

from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations
from shapely.geometry import shape


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

ROOT = Path(__file__).resolve().parent.parent
GEOBASE = ROOT / "geo" / "final"
GEOJSON_FILE = GEOBASE / "capital_cities.geojson"

OUTPUT_DIR = (
    BASE
    / "data"
    / "final"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
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
    "Canberra–Queanbeyan",
]

GROUPS = [
    "Bird",
    "Mammal",
    "Reptile",
    "Insect",
]

YEARS = list(range(2016, 2026))

CHUNK_SIZE = 250_000


# ============================================================
# AGGREGATORS
# ============================================================

# Raw occurrence counts
city_record_counts = Counter()

city_group_record_counts = Counter()

city_year_record_counts = Counter()

family_record_counts = Counter()

species_record_counts = Counter()


# Unique species sets
city_species = defaultdict(set)

city_group_species = defaultdict(set)

city_year_species = defaultdict(set)

family_species = defaultdict(set)

species_cities = defaultdict(set)


# Species metadata
species_group = {}

species_common_name = {}

species_family = {}


# ============================================================
# READ MASTER DATA IN CHUNKS
# ============================================================

USE_COLS = [
    "species",
    "vernacularName",
    "family",
    "animal_group",
    "year",
    "CITY",
]


print("Processing master dataset...\n")

total_rows = 0

for chunk_no, chunk in enumerate(
    pd.read_csv(
        MASTER_FILE,
        usecols=USE_COLS,
        chunksize=CHUNK_SIZE,
        low_memory=False
    ),
    start=1
):

    total_rows += len(chunk)

    # --------------------------------------------------------
    # STANDARDISE YEAR
    # --------------------------------------------------------

    chunk["year"] = pd.to_numeric(
        chunk["year"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # 1. RECORD COUNTS
    # --------------------------------------------------------

    city_record_counts.update(
        chunk["CITY"]
        .value_counts()
        .to_dict()
    )

    city_group_record_counts.update(
        chunk.groupby(
            ["CITY", "animal_group"]
        )
        .size()
        .to_dict()
    )

    city_year_record_counts.update(
        chunk.groupby(
            ["CITY", "year"]
        )
        .size()
        .to_dict()
    )

    # ========================================================
    # SPECIES-LEVEL DATA ONLY
    #
    # All richness calculations use records where species
    # identification exists.
    # ========================================================

    species_rows = chunk[
        chunk["species"].notna()
    ].copy()

    # --------------------------------------------------------
    # 2. CITY SPECIES SETS
    # --------------------------------------------------------

    for city, values in species_rows.groupby("CITY")["species"]:

        city_species[city].update(
            values.unique()
        )

    # --------------------------------------------------------
    # 3. CITY × GROUP SPECIES SETS
    # --------------------------------------------------------

    for key, values in species_rows.groupby(
        ["CITY", "animal_group"]
    )["species"]:

        city_group_species[key].update(
            values.unique()
        )

    # --------------------------------------------------------
    # 4. CITY × YEAR SPECIES SETS
    # --------------------------------------------------------

    for key, values in species_rows.groupby(
        ["CITY", "year"]
    )["species"]:

        city_year_species[key].update(
            values.unique()
        )

    # --------------------------------------------------------
    # 5. FAMILY / TAXONOMY
    # --------------------------------------------------------

    family_rows = species_rows[
        species_rows["family"].notna()
    ]

    for key, values in family_rows.groupby(
        ["animal_group", "family"]
    )["species"]:

        family_species[key].update(
            values.unique()
        )

    family_record_counts.update(
        family_rows.groupby(
            ["animal_group", "family"]
        )
        .size()
        .to_dict()
    )

    # --------------------------------------------------------
    # 6. SPECIES RECORD COUNTS
    # --------------------------------------------------------

    species_record_counts.update(
        species_rows["species"]
        .value_counts()
        .to_dict()
    )

    # --------------------------------------------------------
    # 7. NUMBER OF CITIES EACH SPECIES OCCURS IN
    # --------------------------------------------------------

    for sp, values in species_rows.groupby(
        "species"
    )["CITY"]:

        species_cities[sp].update(
            values.unique()
        )

    # --------------------------------------------------------
    # 8. SPECIES → GROUP
    # --------------------------------------------------------

    first_group = (
        species_rows[
            ["species", "animal_group"]
        ]
        .drop_duplicates("species")
    )

    for _, row in first_group.iterrows():

        species_group.setdefault(
            row["species"],
            row["animal_group"]
        )

    # --------------------------------------------------------
    # 9. SPECIES → FAMILY
    # --------------------------------------------------------

    first_family = (
        species_rows[
            species_rows["family"].notna()
        ][
            ["species", "family"]
        ]
        .drop_duplicates("species")
    )

    for _, row in first_family.iterrows():

        species_family.setdefault(
            row["species"],
            row["family"]
        )

    # --------------------------------------------------------
    # 10. SPECIES → COMMON NAME
    # --------------------------------------------------------

    common_rows = species_rows[
        species_rows["vernacularName"].notna()
    ].copy()

    common_rows["vernacularName"] = (
        common_rows["vernacularName"]
        .astype(str)
        .str.strip()
    )

    common_rows = common_rows[
        common_rows["vernacularName"] != ""
    ]

    common_rows = common_rows[
        ["species", "vernacularName"]
    ].drop_duplicates("species")

    for _, row in common_rows.iterrows():

        species_common_name.setdefault(
            row["species"],
            row["vernacularName"]
        )

    print(
        f"Chunk {chunk_no}: "
        f"{total_rows:,} rows processed"
    )


print("\nAggregation complete.")


# ============================================================
# LOAD CITY GEOMETRY AND CREATE DISPLAY POINTS
# ============================================================

with open(
    GEOJSON_FILE,
    "r",
    encoding="utf-8"
) as f:

    city_geojson = json.load(f)


city_locations = {}


for feature in city_geojson["features"]:

    city = feature["properties"]["CITY"]

    geom = shape(
        feature["geometry"]
    )

    # representative_point() is guaranteed to fall inside
    # the polygon and works well for proportional symbols.
    point = geom.representative_point()

    city_locations[city] = {
        "longitude": point.x,
        "latitude": point.y
    }


# ============================================================
# DATASET 01
# CITY SUMMARY
# Used for proportional-symbol map
# ============================================================

rows = []

for city in CITIES:

    row = {
        "city": city,

        "longitude":
            city_locations[city]["longitude"],

        "latitude":
            city_locations[city]["latitude"],

        "record_count":
            city_record_counts[city],

        "species_richness":
            len(city_species[city]),
    }

    for group in GROUPS:

        column_name = (
            group.lower()
            + "_species"
        )

        row[column_name] = len(
            city_group_species[
                (city, group)
            ]
        )

    rows.append(row)


city_summary = pd.DataFrame(rows)


city_summary.to_csv(
    OUTPUT_DIR / "01_city_summary.csv",
    index=False
)


# ============================================================
# DATASET 02
# CITY × ANIMAL GROUP
# Used for heatmap
# ============================================================

rows = []

for city in CITIES:

    for group in GROUPS:

        rows.append({

            "city": city,

            "animal_group": group,

            "record_count":
                city_group_record_counts[
                    (city, group)
                ],

            "species_richness":
                len(
                    city_group_species[
                        (city, group)
                    ]
                )
        })


city_group_summary = pd.DataFrame(rows)


city_group_summary.to_csv(
    OUTPUT_DIR
    / "02_city_group_summary.csv",
    index=False
)


# ============================================================
# DATASET 03
# TAXONOMIC COMPOSITION — FAMILY LEVEL
# Used for treemap
# ============================================================

rows = []

for (group, family), species_set in (
    family_species.items()
):

    rows.append({

        "animal_group": group,

        "family": family,

        "species_richness":
            len(species_set),

        "record_count":
            family_record_counts[
                (group, family)
            ]
    })


taxonomy_family = pd.DataFrame(rows)


taxonomy_family = taxonomy_family.sort_values(
    [
        "animal_group",
        "species_richness"
    ],
    ascending=[
        True,
        False
    ]
)


taxonomy_family.to_csv(
    OUTPUT_DIR
    / "03_taxonomy_treemap.csv",
    index=False
)


# ============================================================
# DATASET 03B
# OPTIONAL SPECIES-LEVEL TAXONOMY
#
# Useful later if you want species tooltips/drill-down.
# ============================================================

rows = []

for sp, count in species_record_counts.items():

    rows.append({

        "animal_group":
            species_group.get(sp),

        "family":
            species_family.get(sp),

        "species":
            sp,

        "common_name":
            species_common_name.get(
                sp,
                ""
            ),

        "value": 1,

        "record_count":
            count
    })


taxonomy_species = pd.DataFrame(rows)


taxonomy_species.to_csv(
    OUTPUT_DIR
    / "03b_taxonomy_species.csv",
    index=False
)


# ============================================================
# DATASET 04
# CITY × YEAR SPECIES RICHNESS
# Used for bump chart
# ============================================================

rows = []


for year in YEARS:

    year_rows = []

    for city in CITIES:

        richness = len(
            city_year_species[
                (city, year)
            ]
        )

        records = (
            city_year_record_counts[
                (city, year)
            ]
        )

        year_rows.append({

            "year": year,

            "city": city,

            "species_richness":
                richness,

            "record_count":
                records
        })

    # --------------------------------------------------------
    # Rank cities:
    #
    # Primary:
    # higher species richness
    #
    # Secondary:
    # higher record count
    #
    # Third:
    # alphabetical city
    #
    # This ensures ranks 1–8 remain unique for bump chart.
    # --------------------------------------------------------

    year_rows = sorted(
        year_rows,
        key=lambda x: (
            -x["species_richness"],
            -x["record_count"],
            x["city"]
        )
    )

    for rank, row in enumerate(
        year_rows,
        start=1
    ):

        row["rank"] = rank

        rows.append(row)


city_year_richness = pd.DataFrame(rows)


city_year_richness.to_csv(
    OUTPUT_DIR
    / "04_city_year_richness.csv",
    index=False
)


# ============================================================
# DATASET 05
# SPECIES CITY COVERAGE
#
# Used for:
# - Ranked bar chart
# - Potential beeswarm chart later
# ============================================================

rows = []


for sp, cities in species_cities.items():

    rows.append({

        "species": sp,

        "common_name":
            species_common_name.get(
                sp,
                ""
            ),

        "animal_group":
            species_group.get(
                sp,
                ""
            ),

        "cities_present":
            len(cities),

        "city_list":
            " | ".join(
                sorted(cities)
            ),

        "record_count":
            species_record_counts[sp]
    })


species_city_coverage = pd.DataFrame(rows)


species_city_coverage = (
    species_city_coverage
    .sort_values(
        [
            "cities_present",
            "record_count"
        ],
        ascending=[
            False,
            False
        ]
    )
)


species_city_coverage.to_csv(
    OUTPUT_DIR
    / "05_species_city_coverage.csv",
    index=False
)


# ============================================================
# DATASET 06
# NETWORK NODES
# ============================================================

rows = []


for city in CITIES:

    rows.append({

        "city":
            city,

        "species_richness":
            len(
                city_species[city]
            ),

        "record_count":
            city_record_counts[city],

        "longitude":
            city_locations[city][
                "longitude"
            ],

        "latitude":
            city_locations[city][
                "latitude"
            ]
    })


network_nodes = pd.DataFrame(rows)


network_nodes.to_csv(
    OUTPUT_DIR
    / "06_network_nodes.csv",
    index=False
)


# ============================================================
# DATASET 07
# NETWORK EDGES
# ============================================================

rows = []


for source, target in combinations(
    CITIES,
    2
):

    shared_all = len(
        city_species[source]
        &
        city_species[target]
    )

    row = {

        "source":
            source,

        "target":
            target,

        "shared_species":
            shared_all
    }

    # Also calculate shared species by group.
    # Useful for richer tooltips / possible filters.

    for group in GROUPS:

        source_set = (
            city_group_species[
                (source, group)
            ]
        )

        target_set = (
            city_group_species[
                (target, group)
            ]
        )

        column = (
            "shared_"
            + group.lower()
        )

        row[column] = len(
            source_set
            &
            target_set
        )

    rows.append(row)


network_edges = pd.DataFrame(rows)


network_edges.to_csv(
    OUTPUT_DIR
    / "07_network_edges.csv",
    index=False
)


# ============================================================
# PRINT SUMMARY
# ============================================================

print("\n====================================")
print("FINAL DATASETS CREATED")
print("====================================")

for file in sorted(
    OUTPUT_DIR.glob("*.csv")
):

    df = pd.read_csv(file)

    print(
        f"{file.name}: "
        f"{len(df):,} rows"
    )


print("\nDONE.")