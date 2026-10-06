"use strict";

/*
=========================================================
WILD CITIES
Visualisation loader
=========================================================
*/

const visualisations = [
  {
    container: "#symbol-map",
    spec: "charts/01_symbol_map.vg.json"
  },

  {
    container: "#group-heatmap",
    spec: "charts/02_heatmap.vg.json"
  },

  {
    container: "#effort-scatter",
    spec: "charts/03_scatter.vg.json"
  },

  // {
  //   container: "#taxonomy-treemap",
  //   spec: "charts/04_treemap.vg.json"
  // },

  {
    container: "#species-ranking",
    spec: "charts/05_species_rank.vg.json"
  },

  {
    container: "#alluvial",
    spec: "charts/06_alluvial.vg.json"
  },

  {
    container: "#bump-chart",
    spec: "charts/07_bump.vg.json"
  },

  {
    container: "#spiral-chart",
    spec: "charts/08_spiral.vg.json"
  },

  {
    container: "#city-network",
    spec: "charts/09_network.vg.json"
  },

  {
    container: "#bin-map",
    spec: "charts/10_bin_map.vg.json"
  },

  {
    container: "#threatened-dot-map",
    spec: "charts/11_threatened_dot_map.vg.json"
  },

  {
    container: "#threatened-choropleth",
    spec: "charts/12_threatened_choropleth.vg.json"
  }
];

/*
=========================================================
Embed one visualisation
=========================================================
*/

function embedVisualisation(item) {
  return vegaEmbed(
    item.container,
    item.spec,
    WILD_CITIES_CONFIG.embedOptions
  ).catch(function (error) {
    console.error(`Failed to load ${item.spec}`, error);
  });
}

/*
=========================================================
Embed all visualisations
=========================================================
*/

visualisations.forEach(embedVisualisation);
