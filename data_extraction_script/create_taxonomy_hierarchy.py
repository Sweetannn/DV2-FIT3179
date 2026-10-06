import pandas as pd


# =========================================================
# FILE PATHS
# =========================================================

INPUT = "data/final/03_taxonomy_treemap_top.csv"
OUTPUT = "data/final/03_taxonomy_hierarchy.csv"


# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv(INPUT)


# =========================================================
# VALIDATE COLUMNS
# =========================================================

required_columns = {
    "animal_group",
    "family",
    "species_richness",
    "record_count",
    "family_type"
}

missing_columns = required_columns - set(df.columns)

if missing_columns:
    raise ValueError(
        f"Missing required columns: {sorted(missing_columns)}"
    )


# =========================================================
# ENSURE NUMERIC TYPES
# =========================================================

df["species_richness"] = pd.to_numeric(
    df["species_richness"],
    errors="raise"
)

df["record_count"] = pd.to_numeric(
    df["record_count"],
    errors="raise"
)


# =========================================================
# VALIDATE EXPECTED GROUPS
# =========================================================

group_order = [
    "Bird",
    "Mammal",
    "Reptile",
    "Insect"
]


unexpected_groups = (
    set(df["animal_group"].unique())
    - set(group_order)
)

if unexpected_groups:
    raise ValueError(
        f"Unexpected animal groups: {unexpected_groups}"
    )


# =========================================================
# BUILD EXPLICIT HIERARCHY
# =========================================================

rows = []


# ---------------------------------------------------------
# Root
# ---------------------------------------------------------

rows.append(
    {
        "id": "root",
        "parent": "",
        "node_type": "root",
        "animal_group": "",
        "family": "",
        "species_richness": 0,
        "record_count": 0,
        "family_type": ""
    }
)


# ---------------------------------------------------------
# Animal group nodes
# ---------------------------------------------------------

for group in group_order:

    rows.append(
        {
            "id": f"group|{group}",
            "parent": "root",
            "node_type": "group",
            "animal_group": group,
            "family": "",
            "species_richness": 0,
            "record_count": 0,
            "family_type": ""
        }
    )


# ---------------------------------------------------------
# Family leaf nodes
# ---------------------------------------------------------

for _, row in df.iterrows():

    group = row["animal_group"]
    family = row["family"]

    rows.append(
        {
            "id": f"family|{group}|{family}",
            "parent": f"group|{group}",
            "node_type": "family",
            "animal_group": group,
            "family": family,
            "species_richness": int(
                row["species_richness"]
            ),
            "record_count": int(
                row["record_count"]
            ),
            "family_type": row["family_type"]
        }
    )


# =========================================================
# CREATE OUTPUT DATAFRAME
# =========================================================

hierarchy = pd.DataFrame(rows)


# =========================================================
# VALIDATION
# =========================================================

expected_rows = 1 + len(group_order) + len(df)

if len(hierarchy) != expected_rows:
    raise ValueError(
        f"Unexpected hierarchy row count. "
        f"Expected {expected_rows}, got {len(hierarchy)}"
    )


if hierarchy["id"].duplicated().any():
    duplicates = hierarchy[
        hierarchy["id"].duplicated(
            keep=False
        )
    ]

    raise ValueError(
        "Duplicate hierarchy IDs found:\n"
        f"{duplicates}"
    )


# Check that every non-root parent exists
valid_ids = set(hierarchy["id"])

invalid_parents = hierarchy[
    (hierarchy["parent"] != "")
    &
    (~hierarchy["parent"].isin(valid_ids))
]

if len(invalid_parents) > 0:
    raise ValueError(
        "Invalid parent IDs found:\n"
        f"{invalid_parents}"
    )


# =========================================================
# SAVE
# =========================================================

hierarchy.to_csv(
    OUTPUT,
    index=False
)


# =========================================================
# REPORT
# =========================================================

print(f"Saved: {OUTPUT}")
print(f"Rows: {len(hierarchy)}")
print()

print("Node counts:")
print(
    hierarchy["node_type"]
    .value_counts()
)

print()

print("Family-level richness totals:")
print(
    hierarchy[
        hierarchy["node_type"] == "family"
    ]
    .groupby("animal_group")[
        "species_richness"
    ]
    .sum()
)

print()

print("Preview:")
print(
    hierarchy.head(12)
)