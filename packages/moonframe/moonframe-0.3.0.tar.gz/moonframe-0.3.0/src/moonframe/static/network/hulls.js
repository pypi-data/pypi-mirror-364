/**
 *  A convex hull is the smalest convex shape enclosing a set of points. 
 *  Because each node is grouped according to its filename, we apply convex hulls to the chart 
 *  to make it easier to identify which nodes belong to the same file. 
 *  /!\ due to the opacity settings, this can be costly.
 */
import { AppState } from "./global.js"
import { get_data } from "./main.js"

/* -------------------------------------------------------------------------- */
/*                                    INIT                                    */
/* -------------------------------------------------------------------------- */

/**
 * Set convex hulls.
 * Each node is grouped according to its filename.
 * @param {Object} nodes data
 */
export function setHulls(nodes) {
    // group nodes
    const groupMap = d3.group(nodes, d => d.filename)
    const groupColor = d3.scaleOrdinal()
        .domain([...(new Set(nodes.map(d => d.filename)))])
        .range(d3.schemeObservable10)

    // create convex hulls
    const hulls = d3.select(".hulls")
        .selectAll("path")
        .data(groupMap, d => d[0])
        .join("path")
        .attr("d", d => groupPath(d[1]))
        .attr("id", d => d[0])
        .style("fill", d => groupColor(d[0]))
        .style("stroke", d => groupColor(d[0]))
        .style("stroke-width", d => d[1].length > 1 ? 140 : 1)
        .style("stroke-linejoin", "round")
        .attr("visibility", "hidden")
        // tooltip
        .attr("data-bs-toggle", "tooltip")
        .attr("data-bs-title", d => d[0])
        .attr("data-bs-trigger", "manual")
        .attr("data-bs-custom-class", "custom-tooltip")
        // events
        .on("mouseenter", function (_, d) {
            if (AppState.focusPoint == undefined && !AppState.isItADrag) {
                // set tooltip
                // check before if there isn't a tooltip already
                if (!AppState.groupTooltip) {
                    const thistooltip = new bootstrap.Tooltip(this)
                    thistooltip.show()
                    AppState.groupTooltip = thistooltip
                    document.documentElement.style.setProperty('--tooltip-color', groupColor(d[0]))
                }
                highlightHull(d[0])
            }
        })
        .on("mouseleave", function (event, d) {
            if (!AppState.isItADrag) {
                // reset tooltip
                if (AppState.groupTooltip) {
                    AppState.groupTooltip.dispose()
                    AppState.groupTooltip = undefined
                    document.documentElement.style.setProperty('--tooltip-color', "black")
                }
                // using a timeout for "hoverpoint" because the hull's mouseleave is triggered before the node's mouseenter
                setTimeout(function () {
                    if (AppState.focusPoint === undefined && AppState.hoverpoint === undefined) {
                        resetHulls()
                        // reset main opacity mask
                        d3.select(".fade-mask").attr("visibility", "hidden")
                        d3.selectAll(`[data-id^='node-']`).classed("selectInPath", false)
                        d3.selectAll(".linkline").classed("linkInPath", false)
                    }
                }
                    , 50)
            }
        })
}

/**
 * Get convex hull shape.
 * Convex hulls are created with "d3.polygonHull" function but it only works
 * if nb pts in the group >= 3.
 * For : 
 *    - nb pts == 2 : create 2 fake points (very) close to an existing pts to 
 *                    have nb pts > 3
 *    - nb pts == 1 : set a circular shape instead of a convex hull (fake pts 
 *                    technique creates instability when there is only one 
 *                    existing point)
 * 
 * @param {Object} d group data : [{filename (string) : data (Object)}, ...]
 * @returns shape
 */
function groupPath(d) {
    let fakePoints = []
    // circular shape = avoid instability 
    if (d.length == 1) {
        const r = 60
        return `M ${d[0].x},${d[0].y - r} 
        A ${r},${r} 0 1,0 ${d[0].x},${d[0].y + r}
        A ${r},${r} 0 1,0 ${d[0].x},${d[0].y - r}
        Z`;
    }
    // convex hulls
    if (d.length == 2) {
        fakePoints = [[d[0].x + 0.001, d[0].y - 0.001],
        [d[0].x - 0.001, d[0].y + 0.001]]
    }
    const points = d.map(i => [i.x, i.y])
        .concat(fakePoints)
        .filter(p => isFinite(p[0]) && isFinite(p[1]))
    const hull = d3.polygonHull(points)
    if (!hull) return null

    return "M" + hull.join("L") + "Z";

}

/* -------------------------------------------------------------------------- */
/*                              UPDATE FUNCTIONS                              */
/* -------------------------------------------------------------------------- */

/**
 * Update convex hull position
 * @param {Object} nodes 
 */
export function updateHulls(nodes) {
    const groupMap = d3.group(nodes, d => d.filename)
    const paths = d3.select(".hulls").selectAll("path")
        .data(groupMap)
        .attr("d", d => groupPath(d[1]))
}

/**
 * Show convex hulls. 
 * @param {Object} nodes data
 */
export function showHulls(nodes) {
    updateHulls(nodes)
    resetHulls()
    if (AppState.focusPoint !== undefined) {
        const data = get_data(AppState.focusPoint)
        highlightHull(data.filename)
    }
}

/* -------------------------------------------------------------------------- */
/*                                   EVENTS                                   */
/* -------------------------------------------------------------------------- */


/**
 * performance hack : use opacity mask
 * so order must be set correctly : 
 * (g) view
 * ├── (path) highlighted nodes 
 * ├── (line) highlighted links
 * ├── (g) hull layer
 * |   ├── (rect) opacity mask for hulls (visible)
 * |   └── (path) convex hulls
 * ├── (rect) main opacity mask (visible)
 * ├── (path) others nodes
 * └── (line) others links
 * 
 * @param {*} refname filename on focus
 */
export function highlightHull(refname) {
    // set opacity links & nodes that are not in the hull
    d3.selectAll(".linkline").filter(el => (el.target.filename === refname && el.source.filename === refname)).classed("linkInPath", true)
    d3.selectAll(`[data-id^='node-']`).filter(el => el.filename === refname).classed("selectInPath", true)
    // hulls are hidden
    d3.selectAll(".hulls").selectAll("*").attr("visibility", el => el[0] !== refname ? "hidden" : "visible")

    // set order
    d3.select(".fade-mask").raise().attr("visibility", "visible")
    d3.select("#hullLayer").raise()
    d3.selectAll(".linkInPath").raise()
    d3.selectAll(".selectInPath, .flag").raise()
}

/**
 * Reset recuring convex hulls modification
 */
export function resetHulls() {
    d3.selectAll(".hulls").selectAll("*").attr("visibility", "visible")
    d3.select("#hullLayer").lower()
    d3.select("#hull-mask").attr("visibility", "visible")
}
