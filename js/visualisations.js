"use strict";

const visualisations = [
  {
    container: "#symbol-map",
    spec: "charts/01_symbol_map.vg.json",
    enabled: true
  },

  {
    container: "#group-heatmap",
    spec: "charts/02_heatmap.vg.json",
    enabled: true
  },

  {
    container: "#effort-scatter",
    spec: "charts/03_scatter.vg.json",
    enabled: true
  },

  {
    container: "#species-ranking",
    spec: "charts/05_species_rank.vg.json",
    enabled: true
  },

  {
    container: "#bump-chart",
    spec: "charts/07_bump.vg.json",
    enabled: true
  },

  {
    container: "#connected-dot",
    spec: "charts/13_connected_dot.vg.json",
    enabled: true
  },

  {
    container: "#spiral-chart",
    spec: "charts/08_spiral.vg.json",
    enabled: true
  },

  {
    container: "#city-network",
    spec: "charts/09_network.vg.json",
    enabled: true
  },

  {
    container: "#bin-map",
    spec: "charts/10_bin_map.vg.json",
    enabled: true
  },

  {
    container: "#upset-plot",
    spec: "charts/11_upset.vg.json",
    enabled: true,
    responsiveVega: true
  },

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
