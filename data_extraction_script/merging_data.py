import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INPUT_FILES = [
    ROOT / "data" / "raw" / "ala" / "aves_2016_urban.csv",
    ROOT / "data" / "raw" / "ala" / "aves_2017-2021_urban.csv",
    ROOT / "data" / "raw" / "ala" / "aves_2022-2025_urban.csv",

    ROOT / "data" / "raw" / "ala" / "mammalia_2016-2025_urban.csv",
    ROOT / "data" / "raw" / "ala" / "reptilia_2016-2025_urban.csv",
    ROOT / "data" / "raw" / "ala" / "insecta_2016-2025_urban.csv",
]

OUTPUT_FILE = (
    ROOT
    / "data"
    / "clean"
    / "urban_wildlife_master.csv"
)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

dfs = []

for file in INPUT_FILES:
    print(f"Reading: {file.name}")

    df = pd.read_csv(
        file,
        low_memory=False
    )

    dfs.append(df)

master = pd.concat(
    dfs,
    ignore_index=True
)

# Optional but recommended:
# remove exact duplicated occurrence IDs
before = len(master)

master = master.drop_duplicates(
    subset=["occurrenceID"]
)

after = len(master)

print(f"\nDuplicates removed: {before - after:,}")

# Ensure consistent year type
master["year"] = pd.to_numeric(
    master["year"],
    errors="coerce"
).astype("Int64")

# Save
master.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nDONE")
print(f"Total master rows: {len(master):,}")
print(f"Saved to: {OUTPUT_FILE}")