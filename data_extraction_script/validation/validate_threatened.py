import pandas as pd
from pathlib import Path


BASE = Path(
    r"C:\Users\ann\Desktop\Y3S1\FIT3179\Visualization 2\Github Repo\DV2-FIT3179"
)

FINAL = (
    BASE
    / "data"
    / "final"
)


city = pd.read_csv(
    FINAL
    / "09_threatened_city_summary.csv"
)

matches = pd.read_csv(
    FINAL
    / "09b_threatened_species_matches.csv"
)


print("\n=== CITY SUMMARY ===")
print(city.to_string(index=False))


print("\n=== BASIC CHECK ===")
print("City rows:", len(city))
print(
    "Species rows:",
    len(matches)
)


print("\n=== THREATENED STATUS COUNTS ===")

print(
    matches[
        matches["is_threatened"]
    ]["epbc_status"]
    .value_counts()
)


print("\n=== THREATENED BY ANIMAL GROUP ===")

print(
    matches[
        matches["is_threatened"]
    ]
    .groupby(
        "animal_group"
    )
    .size()
)


print("\n=== SAMPLE MATCHES ===")

print(
    matches[
        matches["is_threatened"]
    ][
        [
            "species",
            "common_name",
            "animal_group",
            "epbc_status",
            "epbc_listed_name"
        ]
    ]
    .head(50)
    .to_string(index=False)
)


print("\n=== CONSISTENCY CHECK ===")

for _, row in city.iterrows():

    category_total = (
        row["critically_endangered"]
        + row["endangered"]
        + row["vulnerable"]
        + row["conservation_dependent"]
    )

    print(
        row["city"],
        "Threatened:",
        row["threatened_species"],
        "| Category total:",
        category_total,
        "| Match:",
        row["threatened_species"]
        == category_total
    )