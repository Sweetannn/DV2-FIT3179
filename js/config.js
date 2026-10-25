"use strict";

const WILD_CITIES_CONFIG = {
  embedOptions: {
    actions: false,
    renderer: "svg",

    config: {
      legend: {
        titleFont: "Source Sans 3",
        titleFontSize: 14,
        titleFontWeight: 600,
        titleColor: "#202622",
        titlePadding: 10,
        labelFont: "Source Sans 3",
        labelFontSize: 12,
        labelColor: "#68706A",
        labelOffset: 10,
        symbolOpacity: 0.72
      }
    }
  },

  /*
  -------------------------------------------------------
  Animal group definitions
  -------------------------------------------------------
  */

  animalGroups: ["Bird", "Mammal", "Reptile", "Insect"],

  /*
  -------------------------------------------------------
  Colours
  -------------------------------------------------------
  */

  colours: {
    bird: "#3978A8",

    mammal: "#C47A3D",

    reptile: "#48875F",

    insect: "#8167A9",

    text: "#202622",

    muted: "#68706A",

    mapBackground: "#ECEEEA"
  },

  cities_colours: {
    "Adelaide": "#472801",
    "Brisbane": "#B52F18",
    "Canberra": "#1E7487",
    "Melbourne": "#47CAE6",
    "Perth": "#122170",
    "Sydney": "#FFB430",
    "Hobart": "#9307b3",
    "Darwin": "#CC025A"
  }
};
