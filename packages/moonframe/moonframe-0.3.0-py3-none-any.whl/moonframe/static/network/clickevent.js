
import { get_data } from "./main.js"
import { AppState } from "./global.js"
import { showTooltip, clearPathHighlight, hideTooltip, onMouseEnter } from "./mouseevent.js"
import { resetHulls, highlightHull } from "./hulls.js"

/* -------------------------------------------------------------------------- */
/*                               EVENT FUNCTION                               */
/* -------------------------------------------------------------------------- */

/**
 * Focus/unfocus any node
 * @param {Object} el node (dom)
 * @param {Object} d  data
 */
export function selectPoint(el, d) {
    // unfocus
    if (AppState.focusPoint == el) {
        d3.select(AppState.focusPoint).classed("select", false)
        AppState.focusPoint = undefined
        d3.select(".orbit-group").selectAll("*").remove()
    }
    // focus
    else {
        setFocus(el, d)
    }

}

/* -------------------------------------------------------------------------- */
/*                           FOCUS/ONFOCUS FUNCTIONS                          */
/* -------------------------------------------------------------------------- */

/**
 * Cleaner way to focus a point
 * @param {Object} el node
 * @param {Object} d data
 */
export function setFocus(el, d) {
    if (AppState.focusPoint !== undefined) {
        // unselect the previous point
        unfocus()
        // mock mouseenter
        if (AppState.isHullVisible) {
            highlightHull(d.filename)
        }
        onMouseEnter.call(el, undefined, d)
        AppState.focusPoint = el
    }
    else {
        AppState.focusPoint = el
    }
    d3.select(el).classed("select", true)
    showCard(el, d)
    showTooltip(el)
    setOrbitingCircles(d)
}

/**
 *  Cleaner way to unfocus a point
 */
export function unfocus() {
    hideTooltip(AppState.focusPoint)
    d3.select(AppState.focusPoint).classed("select", false)
    AppState.focusPoint = undefined
    clearPathHighlight()
    d3.select(".orbit-group").selectAll("*").remove()
    if (AppState.isHullVisible) {
        resetHulls()
    }
}

/* -------------------------------------------------------------------------- */
/*                              ORBITING CIRCLES                              */
/* -------------------------------------------------------------------------- */

/**
 * Set orbiting circles around the focus point.
 * @param {Object} d Data of the node on focus
 */
export function setOrbitingCircles(d) {
    d3.select(".orbit-group").selectAll("*").remove()
    const mainRadius = Math.sqrt(AppState.size(d[AppState.sKey])) + 2
    const radius = Math.sqrt(AppState.size(d[AppState.sKey])) / 10
    // 1/3
    const dotCount = Math.trunc(2 * Math.PI * mainRadius / radius / 3)
    // style
    const color = AppState.isHullVisible ? "white" : AppState.color(d[AppState.cKey])
    const stroke = AppState.isHullVisible ? AppState.color(d[AppState.cKey]) : "white"

    for (let i = 0; i < dotCount; i++) {
        const angle = (2 * Math.PI * i) / dotCount
        d3.select(".orbit-group")
            .append("circle")
            .attr("class", "orbit-dot")
            .attr("cx", Math.cos(angle) * mainRadius)
            .attr("cy", Math.sin(angle) * mainRadius)
            .attr("r", radius)
            .style("stroke", "white")
            .style("stroke-width", "1px")
            .attr("opacity", "0.8")
            .style("fill", AppState.color(d[AppState.cKey]))
        d3.select(".orbit-container").attr("transform", `translate(${d.x},${d.y})`)
    }
}

/* -------------------------------------------------------------------------- */
/*                                    CARD                                    */
/* -------------------------------------------------------------------------- */

/**
 * Show the card (on click)
 * @param {Object} el node
 * @param {Object} d data
 */
export function showCard(el, d) {
    const cardbodyZone = d3.select("#cardbody")
    const card = d3.select("#card")
    const exclude = ["index", "x", "y", "vx", "vy", "fx", "fy"]
    // reset card
    const cardbody = cardbodyZone.html("").append("div").style("margin-top", "-10px")

    for (let key of Object.entries(d)) {
        if (!exclude.includes(key[0])) {
            const row = cardbody.append("div").style("display", "flex")
            row.append("div")
                .html(key[0])
                .style("flex", `0 0 ${100}px`)
                .style("overflow", "hidden")
                .style("text-overflow", "ellipsis")
                .style("white-space", "nowrap")
            if ((Array.isArray(key[1]) && key[1].length === 0) || key[1] === "") {
                row.append("div")
                    .html("None")
                    .style("font-style", "italic")
                    .style("flex", "1")
                    .style("font-weight", "bold")
                    .style("overflow", "hidden")
                    .style("text-overflow", "ellipsis")
                    .style("white-space", "nowrap")
            }
            else {
                row.append("div")
                    .html(key[1])
                    .style("flex", "1")
                    .style("font-weight", "bold")
                    .style("overflow", "hidden")
                    .style("text-overflow", "ellipsis")
                    .style("white-space", "nowrap")

            }
        }
        card.attr("hidden", null)
            .select("#cardheader")
            .html(`${d.name}`)
            .style("background-color", AppState.color(d[AppState.cKey]))
            .style("color", "white")

    }
}