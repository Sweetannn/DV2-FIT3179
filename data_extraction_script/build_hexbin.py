import pandas as pd
import json
import h3

from pathlib import Path
from collections import Counter, defaultdict


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
    / "08_hexbin.geojson"
)


# ============================================================
# SETTINGS
# ============================================================

H3_RESOLUTION = 8

CHUNK_SIZE = 250_000


# ============================================================
# COUNTERS
# ============================================================

total_counts = Counter()

group_counts = Counter()

city_counts = Counter()


print("Building H3 bins...\n")


total_rows = 0


# ============================================================
# PROCESS MASTER FILE
# ============================================================

for chunk_no, chunk in enumerate(

    pd.read_csv(
        MASTER_FILE,
        usecols=[
            "decimalLatitude",
            "decimalLongitude",
            "animal_group",
            "CITY"
        ],
        chunksize=CHUNK_SIZE,
        low_memory=False
    ),

    start=1
):

    chunk["decimalLatitude"] = (
        pd.to_numeric(
            chunk["decimalLatitude"],
            errors="coerce"
        )
    )

    chunk["decimalLongitude"] = (
        pd.to_numeric(
            chunk["decimalLongitude"],
            errors="coerce"
        )
    )

    chunk = chunk.dropna(
        subset=[
            "decimalLatitude",
            "decimalLongitude",
            "CITY",
            "animal_group"
        ]
    ).copy()


    # --------------------------------------------------------
    # CONVERT OCCURRENCES TO H3 CELLS
    # --------------------------------------------------------

    chunk["h3_cell"] = [

        h3.latlng_to_cell(
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
    # COUNTS
    # --------------------------------------------------------

    total_counts.update(
        chunk[
            "h3_cell"
        ]
        .value_counts()
        .to_dict()
    )


    group_counts.update(

        chunk.groupby(
            [
                "h3_cell",
                "animal_group"
            ]
        )
        .size()
        .to_dict()
    )


    city_counts.update(

        chunk.groupby(
            [
                "h3_cell",
                "CITY"
            ]
        )
        .size()
        .to_dict()
    )


    total_rows += len(chunk)

    print(
        f"Chunk {chunk_no}: "
        f"{total_rows:,} records processed"
    )


# ============================================================
# DOMINANT CITY PER HEXAGON
# ============================================================

cities_per_cell = defaultdict(dict)


for (cell, city), count in (
    city_counts.items()
):

    cities_per_cell[
        cell
    ][
        city
    ] = count


dominant_city = {}


for cell, counts in (
    cities_per_cell.items()
):

    dominant_city[
        cell
    ] = max(
        counts,
        key=counts.get
    )


# ============================================================
# BUILD GEOJSON
# ============================================================

features = []


for cell, total in (
    total_counts.items()
):

    boundary = (
        h3.cell_to_boundary(
            cell
        )
    )


    coordinates = [

        [lon, lat]

        for lat, lon
        in boundary
    ]


    # Close polygon ring
    coordinates.append(
        coordinates[0]
    )


    feature = {

        "type":
            "Feature",

        "properties": {

            "h3_cell":
                cell,

            "city":
                dominant_city.get(
                    cell
                ),

            "total_count":
                total,

            "bird_count":
                group_counts[
                    (
                        cell,
                        "Bird"
                    )
                ],

            "mammal_count":
                group_counts[
                    (
                        cell,
                        "Mammal"
                    )
                ],

            "reptile_count":
                group_counts[
                    (
                        cell,
                        "Reptile"
                    )
                ],

            "insect_count":
                group_counts[
                    (
                        cell,
                        "Insect"
                    )
                ],
        },

        "geometry": {

            "type":
                "Polygon",

            "coordinates": [
                coordinates
            ]
        }
    }


    features.append(
        feature
    )


# ============================================================
# WRITE GEOJSON
# ============================================================

geojson = {

    "type":
        "FeatureCollection",

    "features":
        features
}


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        geojson,
        f,
        separators=(",", ":")
    )


print("\nDONE")

print(
    "Records processed:",
    f"{total_rows:,}"
)

print(
    "H3 cells created:",
    f"{len(features):,}"
)

print(
    "Saved to:",
    OUTPUT_FILE
)