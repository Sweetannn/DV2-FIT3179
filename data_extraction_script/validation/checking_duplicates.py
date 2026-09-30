import pandas as pd

FILE = r"data/clean/urban_wildlife_master.csv"

df = pd.read_csv(FILE, low_memory=False)

print("=== OCCURRENCE ID CHECK ===")

print(
    "Missing occurrenceID:",
    df["occurrenceID"].isna().sum()
)

print(
    "Blank occurrenceID:",
    (df["occurrenceID"].astype(str).str.strip() == "").sum()
)

print(
    "Unique occurrenceIDs:",
    df["occurrenceID"].nunique(dropna=True)
)

print(
    "Duplicated non-null occurrenceIDs remaining:",
    df.loc[df["occurrenceID"].notna(), "occurrenceID"]
      .duplicated()
      .sum()
)