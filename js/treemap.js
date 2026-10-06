"use strict";

/* =========================================================
   CHART 4 — REUSABLE TAXONOMIC TREEMAP

   Wild Cities: Who Still Lives Among Us?
   FIT3179 Data Visualisation 2

   Data:
   Top 10 named families for each animal group.

   Encodings:
   Area   = recorded species richness
   Colour = animal group

   Area comparisons are valid within each panel only.

   ========================================================= */

/* =========================================================
   1. SHARED CONFIGURATION
   ========================================================= */

const TREEMAP_CONFIG = {
  dataDirectory: "data/final/treemap_panels/",

  font: "Source Sans 3",

  /* Layout */
  rectangleGap: 3,

  /* Typography */
  familyFontSize: 12,
  countFontSize: 11,

  /* Internal label padding */
  labelPaddingX: 8,
  labelPaddingY: 8,

  /* Minimum rectangle dimensions */
  minLabelHeight: 25,
  minTwoLineHeight: 47,

  /* Approximate text-width allowance */
  characterWidthFactor: 0.58,

  /* Rendering */
  renderer: "svg",

  /* Animal groups */
  groups: [
    {
      key: "bird",
      name: "Bird",
      container: "#bird-treemap",
      summary: "#bird-treemap-summary",
      filename: "bird_treemap.csv",
      color: "#3978A8",
      textColor: "#FFFFFF"
    },

    {
      key: "mammal",
      name: "Mammal",
      container: "#mammal-treemap",
      summary: "#mammal-treemap-summary",
      filename: "mammal_treemap.csv",
      color: "#C47A3D",
      textColor: "#202622"
    },

    {
      key: "reptile",
      name: "Reptile",
      container: "#reptile-treemap",
      summary: "#reptile-treemap-summary",
      filename: "reptile_treemap.csv",
      color: "#48875F",
      textColor: "#FFFFFF"
    },

    {
      key: "insect",
      name: "Insect",
      container: "#insect-treemap",
      summary: "#insect-treemap-summary",
      filename: "insect_treemap.csv",
      color: "#8167A9",
      textColor: "#FFFFFF"
    }
  ]
};

/* =========================================================
   2. SHARED HELPERS
   ========================================================= */

const TREEMAP_NUMBER_FORMATTER = new Intl.NumberFormat("en-AU");

function formatTreemapNumber(value) {
  return TREEMAP_NUMBER_FORMATTER.format(value);
}

/* =========================================================
   3. LOAD AND VALIDATE THE SOURCE DATA
   ========================================================= */

async function loadTreemapData(group) {
  const url = TREEMAP_CONFIG.dataDirectory + group.filename;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Unable to load ${url}: HTTP ${response.status}`);
  }

  const csvText = await response.text();

  /* Parse CSV using the already-loaded Vega library */
  const records = vega.read(csvText, {
    type: "csv"
  });

  const requiredFields = [
    "family",
    "family_type",
    "species_richness",
    "record_count"
  ];

  if (records.length === 0) {
    throw new Error(`${url} contains no records.`);
  }

  for (const field of requiredFields) {
    if (!(field in records[0])) {
      throw new Error(`${url} is missing required field: ${field}`);
    }
  }

  /* Convert numeric fields explicitly */
  const cleaned = records.map((row) => {
    const richness = Number(row.species_richness);
    const count = Number(row.record_count);

    if (
      !Number.isFinite(richness) ||
      !Number.isFinite(count) ||
      richness < 0 ||
      count < 0
    ) {
      throw new Error(`Invalid numeric value in ${url}`);
    }

    return {
      family: String(row.family || "").trim(),
      family_type: String(row.family_type || "").trim(),
      species_richness: richness,
      record_count: count
    };
  });

  /* Select the ten named families */
  const namedFamilies = cleaned
    .filter((row) => row.family_type === "Named family")
    .sort(
      (a, b) =>
        b.species_richness - a.species_richness ||
        a.family.localeCompare(b.family)
    );

  /* Find the aggregated remainder */
  const otherFamilies = cleaned.filter((row) => row.family_type === "Other");

  if (namedFamilies.length !== 10) {
    throw new Error(
      `${group.name}: expected 10 named families, ` +
        `found ${namedFamilies.length}.`
    );
  }

  if (otherFamilies.length !== 1) {
    throw new Error(
      `${group.name}: expected exactly one Other ` +
        `families row, found ${otherFamilies.length}.`
    );
  }

  if (
    new Set(namedFamilies.map((row) => row.family)).size !==
    namedFamilies.length
  ) {
    throw new Error(`${group.name}: duplicate named families found.`);
  }

  /* Calculate actual panel totals */
  const selectedRichness = namedFamilies.reduce(
    (sum, row) => sum + row.species_richness,
    0
  );

  const otherRichness = otherFamilies[0].species_richness;

  const totalRichness = selectedRichness + otherRichness;

  if (totalRichness <= 0) {
    throw new Error(`${group.name}: total richness must be positive.`);
  }

  const coverage = (selectedRichness / totalRichness) * 100;

  /* Build a proper hierarchy in memory */
  const hierarchy = [
    {
      id: "root",
      parent: null,
      family: "",
      species_richness: 0,
      record_count: 0
    },

    ...namedFamilies.map((row, index) => ({
      id: `family-${index + 1}`,
      parent: "root",

      family: row.family,

      species_richness: row.species_richness,
      record_count: row.record_count
    }))
  ];

  return {
    hierarchy,

    selectedRichness,
    totalRichness,
    coverage
  };
}

/* =========================================================
   4. UPDATE PANEL SUMMARY
   ========================================================= */

function updateTreemapSummary(group, data) {
  const element = document.querySelector(group.summary);

  if (!element) {
    return;
  }

  element.textContent =
    `Top 10: ${formatTreemapNumber(data.selectedRichness)} ` +
    `of ${formatTreemapNumber(data.totalRichness)} ` +
    `recorded species (${data.coverage.toFixed(1)}%)`;
}

/* =========================================================
   5. CREATE REUSABLE VEGA SPECIFICATION
   ========================================================= */

function createTreemapSpec(group, data, width, height) {
  const cfg = TREEMAP_CONFIG;

  /*
    Only show full family names when there is enough room.

    No arbitrary number-only fallback is used.

    If a rectangle cannot accommodate the family name,
    its label is hidden. The complete details remain
    accessible through the tooltip.
  */

  const nameFits =
    "(datum.x1 - datum.x0) >= " +
    "(length(datum.family) * " +
    cfg.familyFontSize * cfg.characterWidthFactor +
    " + " +
    (cfg.labelPaddingX * 2 + 8) +
    ")";

  const canShowName =
    "(" + nameFits + ") && " + "(datum.y1 - datum.y0) >= " + cfg.minLabelHeight;

  const canShowCount =
    "(" +
    canShowName +
    ") && " +
    "(datum.y1 - datum.y0) >= " +
    cfg.minTwoLineHeight;

  return {
    "$schema": "https://vega.github.io/schema/vega/v5.json",

    "width": width,
    "height": height,

    "autosize": "none",
    "padding": 0,

    "data": [
      {
        "name": "tree",

        "values": data.hierarchy,

        "transform": [
          {
            "type": "stratify",
            "key": "id",
            "parentKey": "parent"
          },

          {
            "type": "treemap",

            "field": "species_richness",

            "sort": {
              "field": "value",
              "order": "descending"
            },

            "method": "squarify",
            "ratio": 1.2,

            "round": true,

            "paddingInner": cfg.rectangleGap,
            "paddingOuter": 0,

            "size": [{ "signal": "width" }, { "signal": "height" }]
          }
        ]
      },

      {
        "name": "families",

        "source": "tree",

        "transform": [
          {
            "type": "filter",
            "expr": "datum.depth === 1"
          }
        ]
      }
    ],

    "marks": [
      /* ===================================================
         A. FAMILY RECTANGLES
         =================================================== */

      {
        "type": "rect",

        "from": {
          "data": "families"
        },

        "encode": {
          "enter": {
            "x": {
              "field": "x0"
            },

            "y": {
              "field": "y0"
            },

            "x2": {
              "field": "x1"
            },

            "y2": {
              "field": "y1"
            },

            "fill": {
              "value": group.color
            },

            "stroke": {
              "value": "#FFFFFF"
            },

            "strokeWidth": {
              "value": 2
            },

            "tooltip": {
              "signal":
                "{'Animal group': " +
                JSON.stringify(group.name) +
                ", 'Family': datum.family, " +
                "'Recorded species richness': " +
                "format(datum.species_richness, ','), " +
                "'Occurrence records': " +
                "format(datum.record_count, ',')}"
            }
          },

          "update": {
            "fillOpacity": {
              "value": 0.92
            }
          },

          "hover": {
            "fillOpacity": {
              "value": 1
            }
          }
        }
      },

      /* ===================================================
         B. FAMILY LABEL

         Show complete name only if sufficiently large.
         =================================================== */

      {
        "type": "text",

        "from": {
          "data": "families"
        },

        "interactive": false,

        "encode": {
          "enter": {
            "x": {
              "signal": "datum.x0 + " + cfg.labelPaddingX
            },

            "y": {
              "signal": "datum.y0 + " + cfg.labelPaddingY
            },

            "text": {
              "field": "family"
            },

            "font": {
              "value": cfg.font
            },

            "fontSize": {
              "value": cfg.familyFontSize
            },

            "fontWeight": {
              "value": 600
            },

            "fill": {
              "value": group.textColor
            },

            "align": {
              "value": "left"
            },

            "baseline": {
              "value": "top"
            },

            "limit": {
              "signal":
                "max(0, datum.x1 - datum.x0 - " + cfg.labelPaddingX * 2 + ")"
            },

            "opacity": {
              "signal": canShowName + " ? 1 : 0"
            }
          }
        }
      },

      /* ===================================================
         C. SPECIES COUNT

         Display only when family name also fits.
         =================================================== */

      {
        "type": "text",

        "from": {
          "data": "families"
        },

        "interactive": false,

        "encode": {
          "enter": {
            "x": {
              "signal": "datum.x0 + " + cfg.labelPaddingX
            },

            "y": {
              "signal": "datum.y0 + " + (cfg.labelPaddingY + 19)
            },

            "text": {
              "signal": "format(datum.species_richness, ',') + " + "' species'"
            },

            "font": {
              "value": cfg.font
            },

            "fontSize": {
              "value": cfg.countFontSize
            },

            "fontWeight": {
              "value": 400
            },

            "fill": {
              "value": group.textColor
            },

            "align": {
              "value": "left"
            },

            "baseline": {
              "value": "top"
            },

            "opacity": {
              "signal": canShowCount + " ? 1 : 0"
            }
          }
        }
      }
    ],

    "config": {
      "background": null,

      "font": cfg.font
    }
  };
}

/* =========================================================
   6. RENDERING AND RESPONSIVE RESIZING
   ========================================================= */

const treemapInstances = new Map();

async function createTreemapPanel(group) {
  const container = document.querySelector(group.container);

  if (!container) {
    return;
  }

  try {
    /* Load once per panel */
    const data = await loadTreemapData(group);

    updateTreemapSummary(group, data);

    const width = Math.floor(container.clientWidth);
    const height = Math.floor(container.clientHeight);

    if (width <= 0 || height <= 0) {
      throw new Error(`${group.name}: invalid container dimensions.`);
    }

    const spec = createTreemapSpec(group, data, width, height);

    const result = await vegaEmbed(container, spec, {
      actions: false,
      renderer: TREEMAP_CONFIG.renderer,
      tooltip: true
    });

    const instance = {
      element: container,

      view: result.view,

      lastWidth: width,
      lastHeight: height,

      resizing: false,
      pendingResize: false
    };

    treemapInstances.set(group.key, instance);

    /* Responsive resizing without refetching CSV */
    const observer = new ResizeObserver(() => {
      const nextWidth = Math.floor(container.clientWidth);

      const nextHeight = Math.floor(container.clientHeight);

      if (nextWidth <= 0 || nextHeight <= 0) {
        return;
      }

      if (
        nextWidth === instance.lastWidth &&
        nextHeight === instance.lastHeight
      ) {
        return;
      }

      instance.lastWidth = nextWidth;
      instance.lastHeight = nextHeight;

      instance.pendingResize = true;

      if (instance.resizing) {
        return;
      }

      async function applyResize() {
        instance.resizing = true;

        try {
          while (instance.pendingResize) {
            instance.pendingResize = false;

            const currentWidth = instance.lastWidth;
            const currentHeight = instance.lastHeight;

            await instance.view
              .width(currentWidth)
              .height(currentHeight)
              .runAsync();
          }
        } finally {
          instance.resizing = false;
        }
      }

      applyResize().catch((error) => {
        console.error(`Treemap resize failed: ${group.name}`, error);
      });
    });

    observer.observe(container);

    instance.observer = observer;
  } catch (error) {
    console.error(`Failed to render ${group.name} treemap:`, error);

    container.textContent = "Unable to load this visualisation.";
  }
}

/* =========================================================
   7. INITIALISATION
   ========================================================= */

async function initialiseTaxonomyTreemaps() {
  await Promise.all(
    TREEMAP_CONFIG.groups.map((group) => createTreemapPanel(group))
  );
}

/* =========================================================
   8. START AFTER DOM IS READY
   ========================================================= */

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initialiseTaxonomyTreemaps, {
    once: true
  });
} else {
  initialiseTaxonomyTreemaps();
}
