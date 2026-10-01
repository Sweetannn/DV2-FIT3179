import {
    renderHeatmap
} from "./charts/heatmap.js";


async function initialiseCharts() {

    try {

        await renderHeatmap(
            "#heatmap"
        );

    }

    catch (error) {

        console.error(
            "Failed to render visualisations:",
            error
        );

    }
}


document.addEventListener(
    "DOMContentLoaded",
    initialiseCharts
);