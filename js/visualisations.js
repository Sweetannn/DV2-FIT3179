"use strict";

const visualisations = [
  /* Chart 1 : Proportional Symbol Map */
  {
    container: "#symbol-map",
    spec: "charts/01_symbol_map.vg.json",
    enabled: true
  },

  /* Chart 2 : Heatmap */
  {
    container: "#group-heatmap",
    spec: "charts/02_heatmap.vg.json",
    enabled: true
  },

  /* Chart 3 : Scatterplot */
  {
    container: "#effort-scatter",
    spec: "charts/03_scatter.vg.json",
    enabled: true
  },

  /*
    Chart 4 uses js/treemap.js
  */

  /* Chart 5 : Species Coverage Ranking */
  {
    container: "#species-ranking",
    spec: "charts/05_species_rank.vg.json",
    enabled: true
  },

  /* Chart 6 : Alluvial Diagram */
  {
    container: "#alluvial",
    spec: "charts/06_alluvial.vg.json",
    enabled: true,
    responsiveVega: true
  },

  /* Chart 7 : Bump Chart */
  {
    container: "#bump-chart",
    spec: "charts/07_bump.vg.json",
    enabled: true
  },

  /* Chart 8 : Spiral Plot */
  {
    container: "#spiral-chart",
    spec: "charts/08_spiral.vg.json",
    enabled: false
  },

  /* Chart 9 : Network Diagram */
  {
    container: "#city-network",
    spec: "charts/09_network.vg.json",
    enabled: true
  },

  /* Chart 10 : Bin Map */
  {
    container: "#bin-map",
    spec: "charts/10_bin_map.vg.json",
    enabled: false
  },

  /* Chart 11 : Threatened Species Dot-Density Map */
  {
    container: "#threatened-dot-map",
    spec: "charts/11_threatened_dot_density.vg.json",
    enabled: false
  },

  /* Chart 12 : Threatened Species Choropleth */
  {
    container: "#threatened-choropleth",
    spec: "charts/12_threatened_choropleth.vg.json",
    enabled: true
  }
];

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
    const result = await vegaEmbed(
      container,
      item.spec,
      WILD_CITIES_CONFIG.embedOptions
    );

    if (item.responsiveVega) {
      enableResponsiveVega(container, result.view);
    }
  } catch (error) {
    console.error(`Failed to load ${item.spec}`, error);

    container.textContent = "Unable to load this visualisation.";
  }
}

async function initialiseVisualisations() {
  const enabledCharts = visualisations.filter((item) => item.enabled);

  await Promise.all(enabledCharts.map(embedVisualisation));
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initialiseVisualisations, {
    once: true
  });
} else {
  initialiseVisualisations();
}

function enableResponsiveVega(container, view) {
  const parent = container.parentElement;

  let lastWidth = -1;
  let resizeQueue = Promise.resolve();

  const observer = new ResizeObserver((entries) => {
    const width = Math.floor(entries[0].contentRect.width);

    if (width <= 0 || width === lastWidth) {
      return;
    }

    lastWidth = width;

    resizeQueue = resizeQueue
      .then(() => {
        view.width(width);
        return view.runAsync();
      })
      .catch((error) => {
        console.error("Vega resize failed:", error);
      });
  });

  observer.observe(parent);

  return observer;
}
