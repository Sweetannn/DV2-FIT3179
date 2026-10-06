"use strict";

/* =========================================================
   WILD CITIES
   Reusable visualisation loader
   ========================================================= */

const visualisations = [
  /* Chart 1 — Proportional Symbol Map */
  {
    container: "#symbol-map",
    spec: "charts/01_symbol_map.vg.json",
    enabled: true
  },

  /* Chart 2 — Heatmap */
  {
    container: "#group-heatmap",
    spec: "charts/02_heatmap.vg.json",
    enabled: true
  },

  /* Chart 3 — Scatterplot */
  {
    container: "#effort-scatter",
    spec: "charts/03_scatter.vg.json",
    enabled: true
  },

  /*
    Chart 4 uses js/treemap.js independently.
    Do not register it twice.
  */

  /* Chart 5 — Species Coverage Ranking */
  {
    container: "#species-ranking",
    spec: "charts/05_species_rank.vg.json",
    enabled: true
  },

  /* Chart 6 — Alluvial Diagram */
  {
    container: "#alluvial",
    spec: "charts/06_alluvial.vg.json",
    enabled: false
  },

  /* Chart 7 — Bump Chart */
  {
    container: "#bump-chart",
    spec: "charts/07_bump.vg.json",
    enabled: false
  },

  /* Chart 8 — Spiral Plot */
  {
    container: "#spiral-chart",
    spec: "charts/08_spiral.vg.json",
    enabled: false
  },

  /* Chart 9 — Network Diagram */
  {
    container: "#city-network",
    spec: "charts/09_network.vg.json",
    enabled: false
  },

  /* Chart 10 — Bin Map */
  {
    container: "#bin-map",
    spec: "charts/10_bin_map.vg.json",
    enabled: false
  },

  /* Chart 11 — Threatened Species Dot Map */
  {
    container: "#threatened-dot-map",
    spec: "charts/11_threatened_dot_map.vg.json",
    enabled: false
  },

  /* Chart 12 — Threatened Species Choropleth */
  {
    container: "#threatened-choropleth",
    spec: "charts/12_threatened_choropleth.vg.json",
    enabled: false
  }
];

/* =========================================================
   EMBED ONE VISUALISATION
   ========================================================= */

async function embedVisualisation(item) {
  if (!item.enabled) {
    return;
  }

  const container = document.querySelector(item.container);

  if (!container) {
    console.warn(`Chart container not found: ${item.container}`);
    return;
  }

  try {
    await vegaEmbed(container, item.spec, WILD_CITIES_CONFIG.embedOptions);
  } catch (error) {
    console.error(`Failed to load ${item.spec}`, error);

    container.textContent = "Unable to load this visualisation.";
  }
}

/* =========================================================
   INITIALISE CHARTS
   ========================================================= */

async function initialiseVisualisations() {
  const enabledCharts = visualisations.filter((item) => item.enabled);

  await Promise.all(enabledCharts.map(embedVisualisation));
}

/* =========================================================
   START
   ========================================================= */

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initialiseVisualisations, {
    once: true
  });
} else {
  initialiseVisualisations();
}
