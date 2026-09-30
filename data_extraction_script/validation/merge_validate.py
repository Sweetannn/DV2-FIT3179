import pandas as pd

FILE = r"data/clean/urban_wildlife_master.csv"

df = pd.read_csv(
    FILE,
    low_memory=False
)

print("\n=== BASIC ===")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\n=== OCCURRENCE ID ===")

print(
    "Missing occurrenceID:",
    df["occurrenceID"].isna().sum()
)

print(
    "Unique non-null occurrenceID:",
    df["occurrenceID"].nunique(dropna=True)
)

print(
    "Duplicated non-null occurrenceID:",
    df.loc[
        df["occurrenceID"].notna(),
        "occurrenceID"
    ].duplicated().sum()
)

print("\n=== ANIMAL GROUPS ===")
print(df["animal_group"].value_counts())

print("\n=== CLASSES ===")
print(df["class"].value_counts())

print("\n=== YEARS ===")
print(
    df["year"]
    .value_counts()
    .sort_index()
)

print("\n=== CITIES ===")
print(df["CITY"].value_counts())

print("\n=== SPECIES COMPLETENESS ===")

for group in [
    "Bird",
    "Mammal",
    "Reptile",
    "Insect"
]:

    subset = df[
        df["animal_group"] == group
    ]

    percentage = (
        subset["species"]
        .notna()
        .mean()
        * 100
    )

    print(
        f"{group}: {percentage:.2f}% species-level"
    )