import { colorLegend } from "../nobvisualjs/tools/tools_colorLegend.js"
import { AppState } from "./global.js"
import { get_data, setArrow } from "./main.js"

/* -------------------------------------------------------------------------- */
/*                            SCALE INIT FUNCTIONS                            */
/* -------------------------------------------------------------------------- */

/**
 * Create color scale depending on the type of the selected metric (AppState.cKey)
 */
export function createColorLegend(nodes) {
    const log10 = d3.select("#log10_checkbox")
    const domain = [...(new Set(nodes.map(d => d[AppState.cKey])))]

    // continuous scale
    if (typeof domain[0] == "number") {
        log10.attr("disabled", undefined)

        // extent -> get min max
        const [min, max] = d3.extent(domain)
        AppState.color = d3.scaleSequential([min, max], d3.interpolatePlasma)
        if (AppState.isLog) { // log
            AppState.color = d3.scaleSequentialLog(
                [1, max]
                , d3.interpolatePlasma)
        }

        colorLegend({ color: AppState.color })
    }
    // categorical scale
    else {
        log10.attr("disabled", true)
        AppState.color = d3.scaleOrdinal()
            .domain(domain)
            .range(d3.schemeObservable10)

        if (AppState.cKey !== "filename") {
            createCatColorLegend(domain)
        }
    }

}


/**
 * Create a categorical scale
 * @param {Object} color scale
 * @param {Array} domain list of possible values for the selected metric
 */
function createCatColorLegend(domain) {
    const itemHeight = 20
    // d3.select("#colorTitle").html(AppState.cKey)
    const legend = d3.select("#legend")
        .attr("height", itemHeight * (domain.length + 1))
        .attr("viewBox", undefined)
        .append("g")

    let row = -1
    domain.forEach((cat, i) => {
        row += 1

        const group = legend.append("g")
            .attr("id", "otherlegend")
            .attr("transform", `translate(0, ${row * itemHeight})`)

        group.append("rect")
            .attr("width", 10)
            .attr("height", 10)
            .attr("fill", AppState.color(cat))

        group.append("text")
            .attr("x", 14)
            .attr("y", 9)
            .attr("id", `legend-${i}`)
            .text(cat)
            .style("font-size", "14px")
            .style("fill", "#333")
    })

}

/* -------------------------------------------------------------------------- */
/*                               EVENT FUNCTION                               */
/* -------------------------------------------------------------------------- */

/**
 * Updates all color-dependant elements.
 * Is called at the "change"e event of cselector.
 * @param {Object} nodes 
 */
export function changeColor(nodes) {
    const svg = d3.select("svg")
    d3.select("#legend").selectAll("*").remove()
    createColorLegend(nodes)
    svg.selectAll(`[data-id^='node-']`).attr("fill", d => AppState.color(d[AppState.cKey])).style("--fill-color", d => AppState.color(d[AppState.cKey]))
   
    svg.selectAll(".linkline")
        .attr("stroke", d => AppState.color(d.source[AppState.cKey]))
        .attr("marker-end", (d,i) => setArrow(AppState.color(d.source[AppState.cKey]), AppState.size(d.target[AppState.sKey]), i))
   
    if (AppState.focusPoint !== undefined) {
        const data = get_data(AppState.focusPoint)
        d3.select(".orbit-group")
            .selectAll("circle")
            .style("fill", AppState.color(data[AppState.cKey]))
    }
    svg.selectAll(".flag").each(function () {
        const index = d3.select(this).attr("index")
        const data = nodes[index]
        const circle = d3.select(`#circle-flag-${index}`)
            .style("fill", AppState.color(data[AppState.cKey]))
            .style("stroke", AppState.color(data[AppState.cKey]))
    })

}
