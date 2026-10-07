
from pathlib import Path
import csv
import json
from collections import defaultdict


# =========================================================
# CONFIGURATION
# =========================================================

SOURCE = Path("data/final/02_city_group_summary.csv")
OUTPUT = Path("data/final/06_alluvial_data.json")

GROUPS = [
    "Bird",
    "Mammal",
    "Reptile",
    "Insect",
]

CITIES = [
    "Brisbane",
    "Sydney",
    "Melbourne",
    "Canberra–Queanbeyan",
    "Adelaide",
    "Perth",
    "Hobart",
    "Darwin",
]

COLORS = {
    "Bird": "#3978A8",
    "Mammal": "#C47A3D",
    "Reptile": "#48875F",
    "Insect": "#8167A9",
}

# Normalised layout coordinates.
# The final Vega chart converts these to pixels.

GROUP_GAP = 0.035
CITY_GAP = 0.018
TOP_MARGIN = 0.05
BOTTOM_MARGIN = 0.05


# =========================================================
# LOAD DATA
# =========================================================

def load_data():
    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Cannot find source CSV: {SOURCE}"
        )

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        columns = set(reader.fieldnames or [])

    required = {
        "city",
        "animal_group",
        "species_richness",
        "record_count",
    }

    missing = required - columns

    if missing:
        raise ValueError(
            f"Missing CSV columns: {sorted(missing)}"
        )

    values = {}

    for row in rows:
        city = row["city"].strip()
        group = row["animal_group"].strip()

        if city not in CITIES:
            raise ValueError(
                f"Unexpected city: {city}"
            )

        if group not in GROUPS:
            raise ValueError(
                f"Unexpected animal group: {group}"
            )

        key = (city, group)

        if key in values:
            raise ValueError(
                f"Duplicate city–group combination: {key}"
            )

        richness = float(row["species_richness"])
        records = float(row["record_count"])

        if (
            not richness.is_integer()
            or richness < 0
            or not records.is_integer()
            or records < 0
        ):
            raise ValueError(
                f"Invalid numeric data for {key}"
            )

        values[key] = {
            "species_richness": int(richness),
            "record_count": int(records),
        }

    expected = {
        (city, group)
        for city in CITIES
        for group in GROUPS
    }

    if set(values) != expected:
        missing_pairs = expected - set(values)

        raise ValueError(
            f"Missing city–group combinations: "
            f"{sorted(missing_pairs)}"
        )

    return values


# =========================================================
# COMPUTE NODE TOTALS
# =========================================================

def create_alluvial():
    values = load_data()

    group_totals = {
        group: sum(
            values[(city, group)]["species_richness"]
            for city in CITIES
        )
        for group in GROUPS
    }

    city_totals = {
        city: sum(
            values[(city, group)]["species_richness"]
            for group in GROUPS
        )
        for city in CITIES
    }

    grand_total = sum(group_totals.values())

    if grand_total <= 0:
        raise ValueError(
            "Grand total richness must be positive."
        )

    # The available flow height is limited by
    # whichever side has more spacing between nodes.

    usable_height = 1 - TOP_MARGIN - BOTTOM_MARGIN

    group_gap_total = (
        (len(GROUPS) - 1) * GROUP_GAP
    )

    city_gap_total = (
        (len(CITIES) - 1) * CITY_GAP
    )

    flow_height = min(
        usable_height - group_gap_total,
        usable_height - city_gap_total,
    )

    scale = flow_height / grand_total

    group_used = (
        flow_height + group_gap_total
    )

    city_used = (
        flow_height + city_gap_total
    )

    group_cursor = (1 - group_used) / 2
    city_cursor = (1 - city_used) / 2

    nodes = []
    links = []

    group_positions = {}
    city_positions = {}

    # =====================================================
    # LEFT NODES: ANIMAL GROUPS
    # =====================================================

    for group in GROUPS:
        height = group_totals[group] * scale

        group_positions[group] = {
            "y0": group_cursor,
            "y1": group_cursor + height,
        }

        nodes.append({
            "name": group,
            "side": "group",
            "y0": group_cursor,
            "y1": group_cursor + height,
            "total": group_totals[group],
            "color": COLORS[group],
        })

        group_cursor += height + GROUP_GAP

    # =====================================================
    # RIGHT NODES: CITIES
    # =====================================================

    for city in CITIES:
        height = city_totals[city] * scale

        city_positions[city] = {
            "y0": city_cursor,
            "y1": city_cursor + height,
        }

        nodes.append({
            "name": city,
            "side": "city",
            "y0": city_cursor,
            "y1": city_cursor + height,
            "total": city_totals[city],
            "color": "#718879",
        })

        city_cursor += height + CITY_GAP

    # =====================================================
    # RIBBON SEGMENTS
    # =====================================================

    # Source-side ribbons are stacked by city.
    # Target-side ribbons are stacked by animal group.
    #
    # Both ends use the SAME scale, ensuring
    # genuine quantity-preserving ribbons.

    group_offsets = {
        group: group_positions[group]["y0"]
        for group in GROUPS
    }

    city_offsets = {
        city: city_positions[city]["y0"]
        for city in CITIES
    }

    for group in GROUPS:
        for city in CITIES:
            value = values[(city, group)]["species_richness"]

            thickness = value * scale

            sy0 = group_offsets[group]
            sy1 = sy0 + thickness

            ty0 = city_offsets[city]
            ty1 = ty0 + thickness

            group_offsets[group] = sy1
            city_offsets[city] = ty1

            if value == 0:
                continue

            links.append({
                "group": group,
                "city": city,
                "value": value,
                "record_count":
                    values[(city, group)]["record_count"],

                "city_total": city_totals[city],

                "city_share":
                    value / city_totals[city]
                    if city_totals[city] > 0
                    else 0,

                "sy0": sy0,
                "sy1": sy1,
                "ty0": ty0,
                "ty1": ty1,

                "color": COLORS[group],
            })

    # =====================================================
    # VALIDATE FLOW CONSERVATION
    # =====================================================

    for group in GROUPS:
        actual = sum(
            link["value"]
            for link in links
            if link["group"] == group
        )

        assert actual == group_totals[group]

    for city in CITIES:
        actual = sum(
            link["value"]
            for link in links
            if link["city"] == city
        )

        assert actual == city_totals[city]

    assert (
        sum(link["value"] for link in links)
        == grand_total
    )

    # =====================================================
    # WRITE OUTPUT
    # =====================================================

    result = {
        "nodes": nodes,
        "links": links,
        "metadata": {
            "grand_total": grand_total,
            "measure": "city-group species richness",
            "note": (
                "Summed city-group richness is not "
                "national distinct species richness."
            ),
        },
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            result,
            file,
            ensure_ascii=False,
            indent=2
        )

    print(f"Saved: {OUTPUT}")
    print(f"Nodes: {len(nodes)}")
    print(f"Links: {len(links)}")
    print(f"Total city-group richness: {grand_total:,}")

    print("\nCity totals:")
    for city in CITIES:
        print(
            f"  {city}: {city_totals[city]:,}"
        )

    print("\nAnimal group totals:")
    for group in GROUPS:
        print(
            f"  {group}: {group_totals[group]:,}"
        )


if __name__ == "__main__":
    create_alluvial()
