import { setOrbitingCircles } from "./clickevent.js"
import { AppState } from "./global.js"
import { get_data, setArrow } from "./main.js"

/* -------------------------------------------------------------------------- */
/*                            SCALE INIT FUNCTIONS                            */
/* -------------------------------------------------------------------------- */

/**
 * Create a size scale
 * @param {Object} nodes 
 * @returns shift value
 */
export function createSizeScale(nodes) {
    const domain = [...(new Set(nodes.map(d => d[AppState.sKey])))]

    // Use sqrt scale for the size but some domain goes under 0. 
    // so create a shift
    const [min, max] = d3.extent(domain)
    const shift = min < 0 ? -min : 0
    AppState.size = d3.scaleSqrt()
        .domain([min + shift, max + shift])
        .range([500, 5000])

    return shift
}

/* -------------------------------------------------------------------------- */
/*                               EVENT FUNCTION                               */
/* -------------------------------------------------------------------------- */


/**
 * Updates all size-dependent elements.
 * Is called at the "change" event of sselector.
 * @param {Object} nodes
 * @param {Object} targets list of nodes (id) that are targets
 * @param {Object} sources list of nodes (id) that are sources
 */
export function changeSize(nodes, targets, sources) {
    const svg = d3.select("#svg")
    const symbol = d3.symbol()
    const shift = createSizeScale(nodes)

    // update lines
    svg.selectAll(".linkline")
        .attr("marker-end", (d, i) => setArrow(AppState.color(d.source[AppState.cKey]), AppState.size(d.target[AppState.sKey]), i))
        
    // update nodes
    svg.selectAll(`[data-id^='node-']`)
        .attr("d", d => {
            const size = shift + AppState.size(d[AppState.sKey])
            if (!targets.has(d.id)) return symbol.type(d3.symbolStar).size(size)();
            if (!sources.has(d.id)) return symbol.type(d3.symbolSquare).size(size)();
            return symbol.type(d3.symbolCircle).size(size)(); // default
        })

    // update flag
    svg.selectAll(".flag").each(function () {
        const index = d3.select(this).attr("index")
        const data = nodes[index]
        const circle = d3.select(`#circle-flag-${index}`)
            .attr("r", Math.sqrt(AppState.size(data[AppState.sKey])) + 2)
    })

    // update orbiting circles 
    if (AppState.focusPoint !== undefined) {
        const data = get_data(AppState.focusPoint)
        setOrbitingCircles(data)

    }


}