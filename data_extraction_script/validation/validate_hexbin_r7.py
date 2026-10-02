import json
from pathlib import Path
from collections import defaultdict


# ============================================================
# PATH
# ============================================================

BASE = Path(
    r"C:\Users\ann\Desktop\Y3S1\FIT3179\Visualization 2\Github Repo\DV2-FIT3179"
)

FILE = (
    BASE
    / "data"
    / "final"
    / "08_hexbin_r7.geojson"
)


# ============================================================
# LOAD
# ============================================================

with open(
    FILE,
    "r",
    encoding="utf-8"
) as f:

    data = json.load(f)


features = data["features"]


# ============================================================
# BASIC
# ============================================================

print("\n================================")
print("BASIC")
print("================================")

print(
    "Features:",
    f"{len(features):,}"
)


# ============================================================
# EXPECTED TOTALS
# ============================================================

expected_totals = {

    "count_all":
        17_451_697,

    "count_bird":
        15_970_891,

    "count_mammal":
        338_443,

    "count_reptile":
        118_684,

    "count_insect":
        1_023_679
}


# ============================================================
# ACTUAL TOTALS
# ============================================================

actual_totals = {}


for field in expected_totals:

    actual_totals[field] = sum(

        feature[
            "properties"
        ].get(
            field,
            0
        )

        for feature in features
    )


print("\n================================")
print("TOTALS")
print("================================")


for field, actual in actual_totals.items():

    expected = expected_totals[field]

    print(
        f"{field}: "
        f"{actual:,} "
        f"(expected {expected:,}) "
        f"-> {actual == expected}"
    )


# ============================================================
# COMPONENT CHECK
# ============================================================

component_total = (

    actual_totals["count_bird"]
    +
    actual_totals["count_mammal"]
    +
    actual_totals["count_reptile"]
    +
    actual_totals["count_insect"]
)


print("\n================================")
print("COMPONENT CHECK")
print("================================")

print(
    "Sum of animal groups:",
    f"{component_total:,}"
)

print(
    "count_all:",
    f"{actual_totals['count_all']:,}"
)

print(
    "Match:",
    component_total
    ==
    actual_totals["count_all"]
)


# ============================================================
# CITY FEATURE COUNTS
# ============================================================

city_feature_counts = {}


for feature in features:

    city = (
        feature["properties"]
        .get(
            "CITY",
            ""
        )
    )

    city_feature_counts[city] = (
        city_feature_counts.get(
            city,
            0
        )
        + 1
    )


print("\n================================")
print("CITY FEATURE COUNTS")
print("================================")


for city, count in sorted(
    city_feature_counts.items()
):

    print(
        f"{city}: {count}"
    )


# ============================================================
# BLANK CITY CHECK
# ============================================================

blank_city_count = sum(

    1

    for feature in features

    if not str(
        feature["properties"]
        .get(
            "CITY",
            ""
        )
    ).strip()
)


print("\n================================")
print("BLANK CITY CHECK")
print("================================")

print(
    "Features with blank city:",
    blank_city_count
)


# ============================================================
# UNIQUE CITY CHECK
# ============================================================

cities = sorted(
    {
        feature["properties"]
        .get(
            "CITY",
            ""
        )

        for feature in features
    }
)


print("\n================================")
print("UNIQUE CITIES")
print("================================")

print(
    cities
)

print(
    "Count:",
    len(cities)
)


# ============================================================
# PARENT-CITY CHECK
# ============================================================

parent_cities = defaultdict(set)


for feature in features:

    props = feature["properties"]

    parent_cities[
        props["h3_cell"]
    ].add(
        props["CITY"]
    )


multi_city = {

    cell:
        cities

    for cell, cities in parent_cities.items()

    if len(cities) > 1
}


print("\n================================")
print("H3 PARENT / CITY CHECK")
print("================================")

print(
    "H3 parents assigned to multiple cities:",
    len(multi_city)
)


if len(multi_city) > 0:

    print(
        "\nExamples:"
    )

    for cell, cities in list(
        multi_city.items()
    )[:20]:

        print(
            cell,
            cities
        )


# ============================================================
# SAMPLE PROPERTIES
# ============================================================

print("\n================================")
print("SAMPLE PROPERTIES")
print("================================")

for feature in features[:10]:

    print(
        feature["properties"]
    )