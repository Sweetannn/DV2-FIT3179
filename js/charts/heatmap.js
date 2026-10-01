import {
    DATA_PATHS,
    GROUP_ORDER,
    VEGA_CONFIG
} from "../config.js";


export async function renderHeatmap(
    selector
) {

    const spec = {

        $schema:
            "https://vega.github.io/schema/vega-lite/v5.json",


        /* ---------------------------------------------
           Responsive sizing
        --------------------------------------------- */

        width:
            "container",

        height:
            430,


        autosize: {

            type:
                "fit",

            contains:
                "padding",

            resize:
                true
        },


        /* ---------------------------------------------
           Data
        --------------------------------------------- */

        data: {

            url:
                DATA_PATHS.cityGroup,

            format: {
                type:
                    "csv"
            }
        },


        /* ---------------------------------------------
           Heatmap mark
        --------------------------------------------- */

        mark: {

            type:
                "rect",

            cornerRadius:
                4,

            stroke:
                "#ffffff",

            strokeWidth:
                2
        },


        /* ---------------------------------------------
           Encoding
        --------------------------------------------- */

        encoding: {

            x: {

                field:
                    "animal_group",

                type:
                    "nominal",

                sort:
                    GROUP_ORDER,

                title:
                    null,

                axis: {

                    labelAngle:
                        0,

                    labelFontSize:
                        13,

                    labelPadding:
                        8
                }
            },


            y: {

                field:
                    "city",

                type:
                    "nominal",

                sort: {

                    field:
                        "species_richness",

                    op:
                        "sum",

                    order:
                        "descending"
                },

                title:
                    null,

                axis: {

                    labelFontSize:
                        13,

                    labelPadding:
                        8
                }
            },


            color: {

                field:
                    "species_richness",

                type:
                    "quantitative",

                title:
                    "Recorded species",

                scale: {

                    scheme:
                        "yellowgreenblue"
                }
            },


            tooltip: [

                {

                    field:
                        "city",

                    type:
                        "nominal",

                    title:
                        "City"
                },

                {

                    field:
                        "animal_group",

                    type:
                        "nominal",

                    title:
                        "Animal group"
                },

                {

                    field:
                        "species_richness",

                    type:
                        "quantitative",

                    title:
                        "Recorded species",

                    format:
                        ","
                },

                {

                    field:
                        "record_count",

                    type:
                        "quantitative",

                    title:
                        "Occurrence records",

                    format:
                        ","
                }
            ]
        },


        /* ---------------------------------------------
           Shared configuration
        --------------------------------------------- */

        config:
            VEGA_CONFIG
    };


    await vegaEmbed(
        selector,
        spec,
        {

            actions:
                false,

            renderer:
                "svg"
        }
    );
}