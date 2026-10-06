import pandas as pd

INPUT = "data/final/03_taxonomy_treemap_top.csv"
OUTPUT = "data/final/03_taxonomy_hierarchy.csv"

TOP_N = 10

df = pd.read_csv(INPUT)

# Ensure numeric columns
df["species_richness"] = pd.to_numeric(
    df["species_richness"],
    errors="raise"
)

df["record_count"] = pd.to_numeric(
    df["record_count"],
    errors="raise"
)

rows = []

group_order = [
    "Bird",
    "Mammal",
    "Reptile",
    "Insect"
]

for group in group_order:

    group_df = (
        df[df["animal_group"] == group]
        .sort_values(
            "species_richness",
            ascending=False
        )
        .reset_index(drop=True)
    )

    # Top N families
    top = group_df.head(TOP_N).copy()

    for _, row in top.iterrows():

        rows.append(
            {
                "animal_group": group,
                "family": row["family"],
                "species_richness": int(
                    row["species_richness"]
                ),
                "record_count": int(
                    row["record_count"]
                ),
                "family_type": "Named family"
            }
        )

    # All remaining families
    other = group_df.iloc[TOP_N:]

    if len(other) > 0:

        rows.append(
            {
                "animal_group": group,
                "family": "Other families",
                "species_richness": int(
                    other["species_richness"].sum()
                ),
                "record_count": int(
                    other["record_count"].sum()
                ),
                "family_type": "Other"
            }
        )

result = pd.DataFrame(rows)

result.to_csv(
    OUTPUT,
    index=False
)

print(f"Saved: {OUTPUT}")
print(f"Rows: {len(result)}")
print()

print(
    result.groupby("animal_group")[
        "species_richness"
    ].sum()
)

print()
print(result)