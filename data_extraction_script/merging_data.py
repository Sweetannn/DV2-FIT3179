import pandas as pd
from pathlib import Path

BASE = Path(
    r"C:\Users\ann\Desktop\Y3S1\FIT3179\Visualization 2\Github Repo\DV2-FIT3179"
)

INPUT_FILES = [
    BASE / "data" / "raw" / "ala" / "aves_2016_urban.csv",
    BASE / "data" / "raw" / "ala" / "aves_2017-2021_urban.csv",
    BASE / "data" / "raw" / "ala" / "aves_2022-2025_urban.csv",
    BASE / "data" / "raw" / "ala" / "mammalia_2016-2025_urban.csv",
    BASE / "data" / "raw" / "ala" / "reptilia_2016-2025_urban.csv",
    BASE / "data" / "raw" / "ala" / "insecta_2016-2025_urban.csv",
]

OUTPUT_FILE = (
    BASE
    / "data"
    / "clean"
    / "urban_wildlife_master.csv"
)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

# ----------------------------------------
# READ FILES
# ----------------------------------------

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

print("\nRows before deduplication:", f"{len(master):,}")

# ----------------------------------------
# OPTIONAL: remove exact duplicate rows
# ----------------------------------------
# This is safe because every column must be identical.

before_exact = len(master)

master = master.drop_duplicates()

after_exact = len(master)

print(
    "Exact full-row duplicates removed:",
    f"{before_exact - after_exact:,}"
)

# ----------------------------------------
# SAFELY HANDLE occurrenceID
# ----------------------------------------

# Records WITH occurrenceID
with_id = master[
    master["occurrenceID"].notna()
].copy()

# Records WITHOUT occurrenceID
without_id = master[
    master["occurrenceID"].isna()
].copy()

print(
    "Records with occurrenceID:",
    f"{len(with_id):,}"
)

print(
    "Records without occurrenceID:",
    f"{len(without_id):,}"
)

# Remove duplicates ONLY from valid occurrence IDs
before_id = len(with_id)

with_id = with_id.drop_duplicates(
    subset=["occurrenceID"]
)

after_id = len(with_id)

print(
    "Duplicate non-null occurrenceIDs removed:",
    f"{before_id - after_id:,}"
)

# ----------------------------------------
# RECOMBINE
# ----------------------------------------

master = pd.concat(
    [with_id, without_id],
    ignore_index=True
)

# ----------------------------------------
# STANDARDISE YEAR
# ----------------------------------------

master["year"] = pd.to_numeric(
    master["year"],
    errors="coerce"
).astype("Int64")

# ----------------------------------------
# SAVE
# ----------------------------------------

master.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nDONE")
print(
    "Final master rows:",
    f"{len(master):,}"
)
print(
    "Missing occurrenceID retained:",
    f"{master['occurrenceID'].isna().sum():,}"
)
print(
    "Saved to:",
    OUTPUT_FILE
)