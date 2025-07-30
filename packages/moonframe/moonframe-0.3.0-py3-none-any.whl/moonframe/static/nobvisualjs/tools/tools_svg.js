import { zoom, isTransition, onFocus, view } from "./tools_zoom.js"
import { HEIGHT, WIDTH } from "../settings.js"

export let tooltip = undefined

/**
 * Creates circles
 * @param {*} root Packed data
 * @returns circles attributes
*/
export function setCircles(root) {
    // set SVG 
    const svg = d3.select("#svg")
        .append("g")
        .attr("transform", `translate(${WIDTH / 2}, ${HEIGHT / 2})`)
        .attr("id", "main")
        .append("g")

    // create circles
    const node = svg
        .selectAll("circle")
        .data(root.descendants()) // excluding root
        .join("circle")
        .attr("id", (d, i) => `circle-${i}`)
        .attr("fill", d => d.children ? d3.interpolateRgb(d.colorID, "white")(0.8) : d.colorID)
        .attr("stroke", d => d.children ? d.colorID : "black")
        .attr("stroke-width", d => d.children ? 1.5 : 0)
        // tooltip
        .attr("data-bs-toggle", "tooltip")
        .attr("data-bs-title", d => `<b>${d.nameID}</b><br>${d.valueID}`)
        .attr("data-bs-trigger", "manual")
        .attr("data-bs-custom-class", "custom-tooltip")
        .attr("data-bs-placement","bottom")
        .attr("data-bs-html", "true")
        // interaction
        .on("click", (event, d) => {
            event.preventDefault()
            zoom(d, root, node, HEIGHT)
        })
        .on("mouseover", onMouseEnter)
        .on("mouseout", onMouseLeave)


    const mask = svg.append("rect")
        .attr("class", "fade-mask")
        .style("opacity", "0.4")
        .style("pointer-events", "none")
        .style("fill", "white")
        .attr("visibility", "hidden")
        .attr("x", -WIDTH / 2).attr("y", -HEIGHT / 2)
        .attr("width", WIDTH)
        .attr("height", HEIGHT)

    return node
}

/**       
 * Mouseon interaction : show tooltip + increase radius (self+all childrens)
 * @param {*} event Mouseon event.
 * @param {*} d Selected circle.
 */
export function onMouseEnter(event, d) {
    // works only when zoom transition is finished
    if (onFocus !== d && d !== onFocus.parent) {
        d3.select(".fade-mask").attr("visibility", "visible").raise()
        if (d.children) {
            d3.select(this).raise()
            for (let child of d.descendants()) {
                d3.select(`#circle-${child.ID}`).raise()
            }
        }
        else {
            d3.select(`#circle-${d.parent.ID}`).raise()
            for (let child of d.parent.descendants()) {
                d3.select(`#circle-${child.ID}`).raise()
            }
            d3.select(this)
                .transition().duration(300)
                .attr("stroke", "black")
                .attr("stroke-width", 2)

        }
    }
    document.documentElement.style.setProperty('--tooltip-color', d.colorID)
    tooltip = new bootstrap.Tooltip(this)
    tooltip.show()
}

/**
 * Mouseout interaction : hide tooltip + radius back to normal  
 * @param {*} event Mouseout event.
 * @param {*} d Selected circle.
 */
export function onMouseLeave(event, d) {
    const mask = d3.select(".fade-mask")

    // reset to "onFocus" view
    if (d.children) {
        if (!onFocus.children) {
            mask.raise()
            d3.select(`#circle-${onFocus.parent.ID}`).raise()
            for (let child of onFocus.parent.descendants()) {
                d3.select(`#circle-${child.ID}`).raise()
            }
        }
        else {
            mask.attr("visibility", "hidden")
        }
    }
    else {
        if (d !== onFocus) {
            d3.select(this)
                .transition().duration(300)
                .attr("stroke-width", 0)
        }
    }

    tooltip.dispose()

}
