"use strict";

/*
=========================================================
WILD CITIES
Shared project configuration
=========================================================
*/

const WILD_CITIES_CONFIG = {
  /*
  -------------------------------------------------------
  Chart embedding options
  -------------------------------------------------------
  */

  embedOptions: {
    actions: false,
    renderer: "svg"
  },

  /*
  -------------------------------------------------------
  Animal group definitions

  Keep the order identical across the whole visualisation.
  -------------------------------------------------------
  */

  animalGroups: ["Bird", "Mammal", "Reptile", "Insect"],

  /*
  -------------------------------------------------------
  Colours

  These must match the colours used inside Vega-Lite
  specifications.
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
    "Hobart": "#FD5DD8",
    "Darwin": "#CC025A"
  }
};
