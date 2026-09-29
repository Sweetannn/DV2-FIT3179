import pandas as pd

FILE = r"data/raw/ala/aves_2016_urban.csv"

df = pd.read_csv(FILE, low_memory=False)

print("\n=== BASIC CHECK ===")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\n=== CITY COUNTS ===")
print(df["CITY"].value_counts())

print("\n=== CITY SPECIES RICHNESS ===")
print(
    df.groupby("CITY")["species"]
      .nunique()
      .sort_values(ascending=False)
)

print("\n=== YEAR ===")
print(df["year"].value_counts())

print("\n=== CLASS ===")
print(df["class"].value_counts())

print("\n=== OCCURRENCE STATUS ===")
print(df["occurrenceStatus"].value_counts(dropna=False))

print("\n=== MISSING VALUES ===")
for col in [
    "species",
    "scientificName",
    "decimalLatitude",
    "decimalLongitude",
    "coordinateUncertaintyInMeters"
]:
    print(
        col,
        df[col].isna().sum(),
        f"({df[col].isna().mean()*100:.2f}%)"
    )

print("\n=== BASIS OF RECORD ===")
print(df["basisOfRecord"].value_counts(dropna=False).head(20))

print(
    "Species-level identified:",
    df["species"].notna().sum()
)

print(
    "Species-level percentage:",
    df["species"].notna().mean() * 100
)