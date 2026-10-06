import pandas as pd
from pathlib import Path


INPUT = "data/final/03_taxonomy_treemap_top.csv"
OUTPUT_DIR = Path("data/final/treemap_panels")

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


df = pd.read_csv(INPUT)

groups = [
    "Bird",
    "Mammal",
    "Reptile",
    "Insect"
]


for group in groups:

    group_df = (
        df[df["animal_group"] == group]
        .copy()
        .sort_values(
            "species_richness",
            ascending=False
        )
        .reset_index(drop=True)
    )


    rows = [
        {
            "id": "root",
            "parent": "",
            "animal_group": group,
            "family": "",
            "species_richness": 0,
            "record_count": 0,
            "family_type": "root"
        }
    ]


    for _, row in group_df.iterrows():

        rows.append(
            {
                "id": f"{group}|{row['family']}",
                "parent": "root",
                "animal_group": group,
                "family": row["family"],
                "species_richness": int(
                    row["species_richness"]
                ),
                "record_count": int(
                    row["record_count"]
                ),
                "family_type": row["family_type"]
            }
        )


    result = pd.DataFrame(rows)


    filename = (
        OUTPUT_DIR
        / f"{group.lower()}_treemap.csv"
    )


    result.to_csv(
        filename,
        index=False
    )


    print(
        f"{group}: "
        f"{len(result)} rows → {filename}"
    )