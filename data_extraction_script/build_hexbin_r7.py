import json
from pathlib import Path
from collections import defaultdict
import h3


# ============================================================
# PATHS
# ============================================================

BASE = Path(
    r"C:\Users\ann\Desktop\Y3S1\FIT3179\Visualization 2\Github Repo\DV2-FIT3179"
)

INPUT_FILE = (
    BASE
    / "data"
    / "final"
    / "08_hexbin.geojson"
)

OUTPUT_FILE = (
    BASE
    / "data"
    / "final"
    / "08_hexbin_r7.geojson"
)


TARGET_RESOLUTION = 7


# ============================================================
# H3 HELPERS
# ============================================================

def cell_to_parent(cell, resolution):

    if hasattr(h3, "cell_to_parent"):

        return h3.cell_to_parent(
            cell,
            resolution
        )

    return h3.h3_to_parent(
        cell,
        resolution
    )


def cell_to_boundary(cell):

    if hasattr(h3, "cell_to_boundary"):

        boundary = h3.cell_to_boundary(
            cell
        )

    else:

        boundary = h3.h3_to_geo_boundary(
            cell
        )


    # H3:
    # (lat, lon)
    #
    # GeoJSON:
    # [lon, lat]

    coordinates = [

        [
            float(lon),
            float(lat)
        ]

        for lat, lon in boundary
    ]


    # close polygon
    if coordinates[0] != coordinates[-1]:

        coordinates.append(
            coordinates[0]
        )


    return coordinates


# ============================================================
# LOAD INPUT GEOJSON
# ============================================================

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:

    data = json.load(f)


features_in = data["features"]


print(
    "Input features:",
    f"{len(features_in):,}"
)


# ============================================================
# INSPECT PROPERTY NAMES
# ============================================================

first_properties = (
    features_in[0]["properties"]
)


print(
    "\nExisting property names:"
)

print(
    first_properties.keys()
)


# ============================================================
# DETECT H3 FIELD
# ============================================================

h3_candidates = [
    "h3_cell",
    "h3",
    "hex_id",
    "h3_index"
]

h3_field = None


for candidate in h3_candidates:

    if candidate in first_properties:

        h3_field = candidate
        break


if h3_field is None:

    raise ValueError(
        "Could not detect H3 field."
    )


print(
    "\nUsing H3 field:",
    h3_field
)


# ============================================================
# DETECT CITY FIELD
# ============================================================

city_candidates = [
    "CITY",
    "city",
    "City"
]

city_field = None


for candidate in city_candidates:

    if candidate in first_properties:

        city_field = candidate
        break


if city_field is None:

    raise ValueError(
        "Could not detect city field."
    )


print(
    "Using city field:",
    city_field
)


# ============================================================
# DETECT COUNT FIELDS
# ============================================================

possible_count_fields = [

    "total_count",
    "count_all",

    "bird_count",
    "count_bird",

    "mammal_count",
    "count_mammal",

    "reptile_count",
    "count_reptile",

    "insect_count",
    "count_insect"
]


count_fields = [

    field

    for field in possible_count_fields

    if field in first_properties
]


print(
    "Count fields:",
    count_fields
)


# ============================================================
# AGGREGATE TO R7
# ============================================================

aggregated = defaultdict(
    lambda: defaultdict(int)
)


for feature in features_in:

    props = feature["properties"]


    child_cell = props[h3_field]


    parent_cell = cell_to_parent(
        child_cell,
        TARGET_RESOLUTION
    )


    city = props.get(
        city_field,
        ""
    )


    key = (
        city,
        parent_cell
    )


    for field in count_fields:

        value = props.get(
            field,
            0
        )


        if value is None:

            value = 0


        aggregated[key][field] += int(
            value
        )


# ============================================================
# FIELD MAPPING
# ============================================================

field_mapping = {

    "total_count":
        "count_all",

    "count_all":
        "count_all",

    "bird_count":
        "count_bird",

    "count_bird":
        "count_bird",

    "mammal_count":
        "count_mammal",

    "count_mammal":
        "count_mammal",

    "reptile_count":
        "count_reptile",

    "count_reptile":
        "count_reptile",

    "insect_count":
        "count_insect",

    "count_insect":
        "count_insect"
}


# ============================================================
# BUILD OUTPUT GEOJSON
# ============================================================

features_out = []


for (
    city,
    parent_cell
), values in aggregated.items():

    properties = {

        "CITY":
            city,

        "h3_cell":
            parent_cell
    }


    for original_field, value in values.items():

        output_field = field_mapping[
            original_field
        ]

        properties[
            output_field
        ] = value


    geometry = {

        "type":
            "Polygon",

        "coordinates": [

            cell_to_boundary(
                parent_cell
            )

        ]
    }


    features_out.append({

        "type":
            "Feature",

        "properties":
            properties,

        "geometry":
            geometry
    })


# ============================================================
# OUTPUT
# ============================================================

output = {

    "type":
        "FeatureCollection",

    "features":
        features_out
}


# ============================================================
# SAVE
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        output,
        f,
        separators=(
            ",",
            ":"
        )
    )


# ============================================================
# REPORT
# ============================================================

print(
    "\n========================================"
)

print(
    "R7 HEXBIN CREATED"
)

print(
    "========================================"
)


print(
    "Input bins:",
    f"{len(features_in):,}"
)

print(
    "Output bins:",
    f"{len(features_out):,}"
)


print(
    "\nSaved to:"
)

print(
    OUTPUT_FILE
)