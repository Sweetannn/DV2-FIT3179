export const DATA_PATHS = {

    citySummary:
        "data/final/01_city_summary.csv",

    cityGroup:
        "data/final/02_city_group_summary.csv",

    taxonomy:
        "data/final/03_taxonomy_treemap.csv",

    taxonomySpecies:
        "data/final/03b_taxonomy_species.csv",

    cityYear:
        "data/final/04_city_year_richness.csv",

    speciesCoverage:
        "data/final/05_species_city_coverage.csv",

    networkNodes:
        "data/final/06_network_nodes.csv",

    networkEdges:
        "data/final/07_network_edges.csv",

    hexbin:
        "data/final/08_hexbin.geojson",

    threatenedCity:
        "data/final/09_threatened_city_summary.csv",

    threatenedSpecies:
        "data/final/09b_threatened_species_matches.csv",

    cityGeoJSON:
        "capital_cities.geojson"
};


export const GROUP_ORDER = [
    "Bird",
    "Mammal",
    "Reptile",
    "Insect"
];


export const GROUP_COLOURS = [
    "#587c58",
    "#9a6642",
    "#75733e",
    "#b98945"
];


export const CITY_ORDER = [
    "Brisbane",
    "Sydney",
    "Melbourne",
    "Canberra–Queanbeyan",
    "Adelaide",
    "Perth",
    "Hobart",
    "Darwin"
];


export const VEGA_CONFIG = {

    background:
        null,

    font:
        "Arial",

    view: {
        stroke:
            null
    },

    axis: {

        labelFont:
            "Arial",

        titleFont:
            "Arial",

        labelColor:
            "#4f554f",

        titleColor:
            "#20251f",

        domainColor:
            "#bfc3bc",

        tickColor:
            "#bfc3bc",

        gridColor:
            "#e7e7e1"
    },

    legend: {

        labelFont:
            "Arial",

        titleFont:
            "Arial",

        labelColor:
            "#4f554f",

        titleColor:
            "#20251f"
    },

    title: {

        font:
            "Georgia",

        color:
            "#20251f"
    }
};