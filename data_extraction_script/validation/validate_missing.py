import pandas as pd
from pathlib import Path

BASE = Path(
    r"C:\Users\ann\Desktop\Y3S1\FIT3179\Visualization 2\Github Repo\DV2-FIT3179"
)

FILES = [
    BASE / "data/raw/ala/aves_2016_urban.csv",
    BASE / "data/raw/ala/aves_2017-2021_urban.csv",
    BASE / "data/raw/ala/aves_2022-2025_urban.csv",
    BASE / "data/raw/ala/mammalia_2016-2025_urban.csv",
    BASE / "data/raw/ala/reptilia_2016-2025_urban.csv",
    BASE / "data/raw/ala/insecta_2016-2025_urban.csv",
]

for file in FILES:

    print(f"\n=== {file.name} ===")

    df = pd.read_csv(
        file,
        usecols=["occurrenceID"],
        low_memory=False
    )

    missing = df["occurrenceID"].isna().sum()

    duplicated = (
        df.loc[df["occurrenceID"].notna(), "occurrenceID"]
          .duplicated()
          .sum()
    )

    print("Rows:", len(df))
    print("Missing occurrenceID:", missing)
    print("Duplicated non-null IDs:", duplicated)