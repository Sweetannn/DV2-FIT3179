import pandas as pd

FILE = r"data/raw/ala/insecta_2016-2025_urban.csv"

df = pd.read_csv(FILE, low_memory=False)

print("\n=== BASIC CHECK ===")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\n=== YEARS ===")
print(df["year"].value_counts().sort_index())

print("\n=== CITY COUNTS ===")
print(df["CITY"].value_counts())

print("\n=== CITY SPECIES RICHNESS ===")
print(
    df.groupby("CITY")["species"]
      .nunique()
      .sort_values(ascending=False)
)

print("\n=== CLASS ===")
print(df["class"].value_counts())

print("\n=== STATUS ===")
print(df["occurrenceStatus"].value_counts(dropna=False))

print("\n=== SPECIES IDENTIFICATION ===")
print(
    "Species-level identified:",
    df["species"].notna().sum()
)

print(
    "Species-level percentage:",
    df["species"].notna().mean() * 100
)