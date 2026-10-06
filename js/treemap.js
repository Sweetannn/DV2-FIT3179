"use strict";

/* =========================================================
   CHART 4 — TOP 5 TAXONOMIC TREEMAPS

   Wild Cities: Who Still Lives Among Us?
   FIT3179 Data Visualisation 2

   One reusable Vega specification for four animal groups.

   Area:
     Recorded species richness among the selected families.

   Colour:
     Animal group.

   Comparison:
     Within-panel only.

   ========================================================= */

/* =========================================================
   1. SHARED CONFIGURATION
   ========================================================= */

const TREEMAP_CONFIG = {
  dataDirectory: "data/final/treemap_panels/",

  /* Change this to 6, 8 or 10 if needed later */
  topN: 5,

  font: "Source Sans 3",

  /* Layout */
  rectangleGap: 2,
  treemapRatio: 1.2,

  /* Typography */
  familyFontSize: 11,
  countFontSize: 10,

  /* Internal padding */
  labelPaddingX: 7,
  labelPaddingY: 7,

  /* Minimum heights */
  minLabelHeight: 24,
  minTwoLineHeight: 43,

  /* Additional horizontal safety margin */
  labelSafetyMargin: 4,

  renderer: "svg",

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

const treemapNumberFormatter = new Intl.NumberFormat("en-AU");

function formatTreemapNumber(value) {
  return treemapNumberFormatter.format(value);
}

/* =========================================================
   3. MEASURE TEXT WIDTH ACCURATELY
   ========================================================= */

/*
  Use the browser's actual font measurements rather than
  estimating text width from character count.

  This helps prevent truncated scientific family names.
*/

const treemapMeasureCanvas = document.createElement("canvas");

const treemapMeasureContext = treemapMeasureCanvas.getContext("2d");

function measureTreemapText(text, fontSize, fontWeight) {
  if (!treemapMeasureContext) {
    throw new Error("Canvas text measurement is unavailable.");
  }

  treemapMeasureContext.font = `${fontWeight} ${fontSize}px "${TREEMAP_CONFIG.font}"`;

  return treemapMeasureContext.measureText(String(text)).width;
}

/* =========================================================
   4. LOAD AND VALIDATE PANEL DATA
   ========================================================= */

async function loadTreemapData(group) {
  const cfg = TREEMAP_CONFIG;

  const url = cfg.dataDirectory + group.filename;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to load ${url}: HTTP ${response.status}`);
  }

  const csvText = await response.text();

  const records = vega.read(csvText, {
    type: "csv"
  });

  if (records.length === 0) {
    throw new Error(`${url} contains no records.`);
  }

  /* Validate required columns */
  const requiredFields = [
    "family",
    "family_type",
    "species_richness",
    "record_count"
  ];

  for (const field of requiredFields) {
    if (!(field in records[0])) {
      throw new Error(`${url}: missing column ${field}`);
    }
  }

  /* Convert numeric values explicitly */
  const cleaned = records.map((row) => {
    const richness = Number(row.species_richness);

    const recordCount = Number(row.record_count);

    if (
      !Number.isFinite(richness) ||
      !Number.isFinite(recordCount) ||
      richness < 0 ||
      recordCount < 0
    ) {
      throw new Error(`${url}: invalid numeric value.`);
    }

    return {
      family: String(row.family || "").trim(),

      family_type: String(row.family_type || "").trim(),

      species_richness: richness,

      record_count: recordCount
    };
  });

  /* Retrieve ALL named families in the source file */
  const allNamedFamilies = cleaned
    .filter((row) => row.family_type === "Named family")
    .sort(
      (a, b) =>
        b.species_richness - a.species_richness ||
        a.family.localeCompare(b.family)
    );

  const otherFamilies = cleaned.filter((row) => row.family_type === "Other");

  /* Validate existing Top 10 + Other dataset */
  if (otherFamilies.length !== 1) {
    throw new Error(`${group.name}: expected one Other families row.`);
  }

  if (allNamedFamilies.length < cfg.topN) {
    throw new Error(`${group.name}: insufficient named families.`);
  }

  if (
    new Set(allNamedFamilies.map((row) => row.family)).size !==
    allNamedFamilies.length
  ) {
    throw new Error(`${group.name}: duplicate family names found.`);
  }

  /* Select Top N for plotting */
  const selectedFamilies = allNamedFamilies.slice(0, cfg.topN);

  /* Correct denominator:
     ALL named families in this CSV + original Other.
  */
  const allNamedRichness = allNamedFamilies.reduce(
    (sum, row) => sum + row.species_richness,
    0
  );

  const totalRichness = allNamedRichness + otherFamilies[0].species_richness;

  /* Numerator:
     Selected Top N only.
  */
  const selectedRichness = selectedFamilies.reduce(
    (sum, row) => sum + row.species_richness,
    0
  );

  if (
    totalRichness <= 0 ||
    selectedRichness <= 0 ||
    selectedRichness > totalRichness
  ) {
    throw new Error(`${group.name}: invalid richness totals.`);
  }

  const coverage = (selectedRichness / totalRichness) * 100;

  /* Build hierarchy for Vega */
  const hierarchy = [
    {
      id: "root",
      parent: null,

      family: "",

      species_richness: 0,
      record_count: 0,

      labelMinWidth: 0,
      countMinWidth: 0
    },

    ...selectedFamilies.map((row, index) => {
      const familyWidth = measureTreemapText(
        row.family,
        cfg.familyFontSize,
        600
      );

      const countLabel = formatTreemapNumber(row.species_richness) + " species";

      const countWidth = measureTreemapText(countLabel, cfg.countFontSize, 400);

      const horizontalPadding = cfg.labelPaddingX * 2 + cfg.labelSafetyMargin;

      return {
        id: `family-${index + 1}`,
        parent: "root",

        family: row.family,

        species_richness: row.species_richness,
        record_count: row.record_count,

        labelMinWidth: Math.ceil(familyWidth + horizontalPadding),

        countMinWidth: Math.ceil(countWidth + horizontalPadding)
      };
    })
  ];

  return {
    hierarchy,

    selectedRichness,
    totalRichness,
    coverage
  };
}

/* =========================================================
   5. UPDATE PANEL SUMMARY
   ========================================================= */

function updateTreemapSummary(group, data) {
  const element = document.querySelector(group.summary);

  if (!element) {
    return;
  }

  element.textContent =
    `Top ${TREEMAP_CONFIG.topN}: ` +
    `${formatTreemapNumber(data.selectedRichness)} ` +
    `of ${formatTreemapNumber(data.totalRichness)} ` +
    `recorded species (${data.coverage.toFixed(1)}%)`;
}

/* =========================================================
   6. UPDATE KEY FINDING WITH ACTUAL COVERAGE
   ========================================================= */

function updateTreemapFinding(results) {
  const element = document.querySelector("#treemap-key-finding-context");

  if (!element) {
    return;
  }

  const sorted = [...results].sort((a, b) => b.coverage - a.coverage);

  const highest = sorted[0];
  const lowest = sorted[sorted.length - 1];

  element.textContent =
    `The top ${TREEMAP_CONFIG.topN} families account for ` +
    `${highest.coverage.toFixed(1)}% of recorded ` +
    `${highest.group.toLowerCase()} richness, compared ` +
    `with ${lowest.coverage.toFixed(1)}% for ` +
    `${lowest.group.toLowerCase()}s. ` +
    `These percentages describe recorded richness ` +
    `in the dataset, not complete biodiversity.`;
}

/* =========================================================
   7. CREATE SHARED VEGA SPECIFICATION
   ========================================================= */

function createTreemapSpec(group, data, width, height) {
  const cfg = TREEMAP_CONFIG;

  /* Show a complete name only if it fits horizontally
     and vertically.
  */
  const showFamilyName =
    "(datum.x1 - datum.x0) >= datum.labelMinWidth " +
    "&& (datum.y1 - datum.y0) >= " +
    cfg.minLabelHeight;

  /* Show the count only if:
     - the complete name fits
     - the count also fits
     - enough height is available for two lines
  */
  const showSpeciesCount =
    "(" +
    showFamilyName +
    ") " +
    "&& (datum.x1 - datum.x0) >= datum.countMinWidth " +
    "&& (datum.y1 - datum.y0) >= " +
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
            "ratio": cfg.treemapRatio,

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
         B. FULL SCIENTIFIC FAMILY NAME
         =================================================== */

      {
        "type": "text",

        "from": {
          "data": "families"
        },

        "interactive": false,

        "encode": {
          "enter": {
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
            }
          },

          "update": {
            "x": {
              "signal": "datum.x0 + " + cfg.labelPaddingX
            },

            "y": {
              "signal": "datum.y0 + " + cfg.labelPaddingY
            },

            "opacity": {
              "signal": "(" + showFamilyName + ") ? 1 : 0"
            }
          }
        }
      },

      /* ===================================================
         C. SPECIES COUNT
         =================================================== */

      {
        "type": "text",

        "from": {
          "data": "families"
        },

        "interactive": false,

        "encode": {
          "enter": {
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
            }
          },

          "update": {
            "x": {
              "signal": "datum.x0 + " + cfg.labelPaddingX
            },

            "y": {
              "signal": "datum.y0 + " + (cfg.labelPaddingY + 18)
            },

            "opacity": {
              "signal": "(" + showSpeciesCount + ") ? 1 : 0"
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
   8. RENDERING AND RESPONSIVE RESIZING
   ========================================================= */

const treemapInstances = new Map();

async function createTreemapPanel(group) {
  const container = document.querySelector(group.container);

  if (!container) {
    throw new Error(`${group.name}: chart container not found.`);
  }

  /* Load the dataset once */
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

    observer: null,

    resizePromise: null
  };

  treemapInstances.set(group.key, instance);

  /* =====================================================
     RESPONSIVE RESIZING
     ===================================================== */

  let requestedWidth = width;
  let requestedHeight = height;

  async function resizeView() {
    if (instance.resizePromise) {
      return instance.resizePromise;
    }

    instance.resizePromise = (async () => {
      while (
        requestedWidth !== instance.lastWidth ||
        requestedHeight !== instance.lastHeight
      ) {
        const targetWidth = requestedWidth;
        const targetHeight = requestedHeight;

        await instance.view.width(targetWidth).height(targetHeight).runAsync();

        instance.lastWidth = targetWidth;
        instance.lastHeight = targetHeight;
      }
    })();

    try {
      await instance.resizePromise;
    } finally {
      instance.resizePromise = null;

      if (
        requestedWidth !== instance.lastWidth ||
        requestedHeight !== instance.lastHeight
      ) {
        resizeView().catch(console.error);
      }
    }
  }

  const observer = new ResizeObserver(() => {
    const nextWidth = Math.floor(container.clientWidth);

    const nextHeight = Math.floor(container.clientHeight);

    if (nextWidth <= 0 || nextHeight <= 0) {
      return;
    }

    requestedWidth = nextWidth;
    requestedHeight = nextHeight;

    if (
      requestedWidth !== instance.lastWidth ||
      requestedHeight !== instance.lastHeight
    ) {
      resizeView().catch((error) => {
        console.error(`Treemap resize failed: ${group.name}`, error);
      });
    }
  });

  observer.observe(container);

  instance.observer = observer;

  return {
    group: group.name,
    coverage: data.coverage
  };
}

/* =========================================================
   9. INITIALISE ALL PANELS
   ========================================================= */

async function initialiseTaxonomyTreemaps() {
  /* Wait for Source Sans 3 to finish loading.
     Text measurements will then match the displayed font.
  */
  if (document.fonts) {
    await document.fonts.ready;
  }

  const results = await Promise.allSettled(
    TREEMAP_CONFIG.groups.map((group) => createTreemapPanel(group))
  );

  const successful = [];

  results.forEach((result, index) => {
    const group = TREEMAP_CONFIG.groups[index];

    if (result.status === "fulfilled") {
      successful.push(result.value);
    } else {
      console.error(`Failed to render ${group.name} treemap:`, result.reason);

      const container = document.querySelector(group.container);

      if (container) {
        container.textContent = "Unable to load this visualisation.";
      }

      const summary = document.querySelector(group.summary);

      if (summary) {
        summary.textContent = "Data unavailable";
      }
    }
  });

  /* Update key finding only when all panels loaded */
  if (successful.length === TREEMAP_CONFIG.groups.length) {
    updateTreemapFinding(successful);
  }
}

/* =========================================================
   10. START WHEN DOM IS READY
   ========================================================= */

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initialiseTaxonomyTreemaps, {
    once: true
  });
} else {
  initialiseTaxonomyTreemaps();
}
