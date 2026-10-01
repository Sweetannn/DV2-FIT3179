import pandas as pd
from pathlib import Path


BASE = Path(
    r"C:\Users\ann\Desktop\Y3S1\FIT3179\Visualization 2\Github Repo\DV2-FIT3179"
)

FINAL = BASE / "data" / "final"


# ============================================================
# CITY SUMMARY
# ============================================================

df = pd.read_csv(
    FINAL / "01_city_summary.csv"
)

print("\n=== 01 CITY SUMMARY ===")
print("Rows:", len(df))
print(df)


# ============================================================
# CITY GROUP
# ============================================================

df = pd.read_csv(
    FINAL / "02_city_group_summary.csv"
)

print("\n=== 02 CITY GROUP ===")
print("Rows:", len(df))

print(
    pd.crosstab(
        df["city"],
        df["animal_group"]
    )
)


# ============================================================
# TREEMAP
# ============================================================

df = pd.read_csv(
    FINAL / "03_taxonomy_treemap.csv"
)

print("\n=== 03 TREEMAP ===")
print("Rows:", len(df))

print(
    df.groupby("animal_group")
      ["species_richness"]
      .sum()
)


# ============================================================
# BUMP
# ============================================================

df = pd.read_csv(
    FINAL / "04_city_year_richness.csv"
)

print("\n=== 04 BUMP ===")
print("Rows:", len(df))

print(
    df.groupby("year")
      .size()
)

print("\nRanks by year:")

print(
    df.groupby("year")
      ["rank"]
      .apply(list)
)


# ============================================================
# SPECIES COVERAGE
# ============================================================

df = pd.read_csv(
    FINAL / "05_species_city_coverage.csv"
)

print("\n=== 05 SPECIES COVERAGE ===")
print("Rows:", len(df))

print("\nTop 15:")
print(
    df.head(15)[
        [
            "species",
            "common_name",
            "animal_group",
            "cities_present",
            "record_count"
        ]
    ]
)


# ============================================================
# NETWORK
# ============================================================

nodes = pd.read_csv(
    FINAL / "06_network_nodes.csv"
)

edges = pd.read_csv(
    FINAL / "07_network_edges.csv"
)

print("\n=== NETWORK ===")
print("Nodes:", len(nodes))
print("Edges:", len(edges))

print("\nLargest shared species links:")

print(
    edges.sort_values(
        "shared_species",
        ascending=False
    ).head(10)
)