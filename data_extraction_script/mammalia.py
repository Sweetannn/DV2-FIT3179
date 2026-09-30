import pandas as pd
import json
from shapely.geometry import shape, Point
from pathlib import Path

# --------------------------------------------------
# PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

INPUT_FOLDER = (
    ROOT
    / "data"
    / "raw"
    / "ala"
    / "Mammalia_2016-2025"
)

GEOBASE = ROOT / "geo" / "final"
GEOJSON_FILE = GEOBASE / "capital_cities.geojson"

OUTPUT_FILE = (
    ROOT
    / "data"
    / "raw"
    / "ala"
    / "mammalia_2016-2025_urban.csv"
)

# --------------------------------------------------
# LOAD CITY POLYGONS
# --------------------------------------------------

with open(GEOJSON_FILE, "r", encoding="utf-8") as f:
    geojson = json.load(f)

cities = []

for feature in geojson["features"]:
    city_name = feature["properties"]["CITY"]
    geometry = shape(feature["geometry"])

    cities.append({
        "city": city_name,
        "geometry": geometry
    })

print("Loaded cities:")
for c in cities:
    print(" -", c["city"])

# --------------------------------------------------
# FIND ALL MAMMALIA CSV PARTS
# --------------------------------------------------

CSV_FILES = sorted(
    INPUT_FOLDER.glob("Mammalia_2016-2025*.csv")
)

print("\nFiles found:", len(CSV_FILES))

for f in CSV_FILES:
    print(" -", f.name)

# --------------------------------------------------
# COLUMNS TO KEEP
# --------------------------------------------------

KEEP_COLUMNS = [
    "occurrenceID",
    "scientificName",
    "vernacularName",
    "species",
    "genus",
    "family",
    "order",
    "class",
    "eventDate",
    "year",
    "month",
    "decimalLatitude",
    "decimalLongitude",
    "coordinateUncertaintyInMeters",
    "occurrenceStatus",
    "basisOfRecord",
    "dataResourceName",
]

# --------------------------------------------------
# PROCESS IN CHUNKS
# --------------------------------------------------

CHUNK_SIZE = 200_000

first_output = True
total_input = 0
total_kept = 0

for csv_file in CSV_FILES:

    print(f"\nProcessing: {csv_file.name}")

    for chunk in pd.read_csv(
        csv_file,
        usecols=lambda c: c in KEEP_COLUMNS,
        chunksize=CHUNK_SIZE,
        low_memory=False
    ):

        total_input += len(chunk)

        # Remove missing coordinates
        chunk = chunk.dropna(
            subset=["decimalLatitude", "decimalLongitude"]
        ).copy()

        # Convert coordinates to numeric
        chunk["decimalLatitude"] = pd.to_numeric(
            chunk["decimalLatitude"],
            errors="coerce"
        )

        chunk["decimalLongitude"] = pd.to_numeric(
            chunk["decimalLongitude"],
            errors="coerce"
        )

        chunk = chunk.dropna(
            subset=["decimalLatitude", "decimalLongitude"]
        )

        # Prepare city field
        chunk["CITY"] = None

        # Point-in-polygon
        for idx, row in chunk.iterrows():

            point = Point(
                row["decimalLongitude"],
                row["decimalLatitude"]
            )

            for city in cities:

                if city["geometry"].covers(point):
                    chunk.at[idx, "CITY"] = city["city"]
                    break

        # Keep only urban records
        urban = chunk[
            chunk["CITY"].notna()
        ].copy()

        urban["animal_group"] = "Mammal"

        total_kept += len(urban)

        # Save progressively
        urban.to_csv(
            OUTPUT_FILE,
            mode="w" if first_output else "a",
            header=first_output,
            index=False
        )

        first_output = False

        print(
            f"Processed: {total_input:,} | "
            f"Urban records kept: {total_kept:,}"
        )

print("\nDONE")
print(f"Total records processed: {total_input:,}")
print(
    f"Records inside 8 urban areas: {total_kept:,}"
)
print(f"Saved to: {OUTPUT_FILE}")