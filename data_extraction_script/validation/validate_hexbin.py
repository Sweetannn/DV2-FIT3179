import json
from pathlib import Path
from collections import Counter


BASE = Path(
    r"C:\Users\ann\Desktop\Y3S1\FIT3179\Visualization 2\Github Repo\DV2-FIT3179"
)

FILE = (
    BASE
    / "data"
    / "final"
    / "08_hexbin.geojson"
)


with open(
    FILE,
    "r",
    encoding="utf-8"
) as f:

    geojson = json.load(f)


features = geojson[
    "features"
]


print(
    "Total hexagons:",
    len(features)
)


total_records = sum(
    f["properties"][
        "total_count"
    ]
    for f in features
)


print(
    "Total occurrence records represented:",
    total_records
)


cities = Counter(

    f["properties"][
        "city"
    ]

    for f in features
)


print("\nHexagons by dominant city:")

for city, count in (
    cities.most_common()
):

    print(
        city,
        count
    )


print("\nGroup count check:")

for group in [
    "bird_count",
    "mammal_count",
    "reptile_count",
    "insect_count"
]:

    total = sum(
        f["properties"][
            group
        ]
        for f in features
    )

    print(
        group,
        total
    )