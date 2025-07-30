import { AppState } from "./global.js"
import { getSourcesLinks, getTargetLinks } from "./main.js"

/* -------------------------------------------------------------------------- */
/*                               EVENT FUNCTION                               */
/* -------------------------------------------------------------------------- */

/**
 * Event "mouseenter"
 * @param {event} event 
 * @param {Object} d data
 */
export function onMouseEnter(event, d) {
    // MouseEnter event only if there isn't a AppState.focusPoint or the select node
    // is part of the AppState.focusPoint path.
    // && it was indeed a mouseEnter not a drag (isItADrag?)
    if ((AppState.focusPoint == undefined
        || d3.select(this).classed("selectInPath") == true)
        && !AppState.isItADrag) {

            if (d3.select(this).classed("flag") === false) {
            showTooltip(this)
        }
        // if there isn't a AppState.focusPoint -> calls highlightPath
        // else, keep the path of the AppState.focusPoint (= change nothing)
        if (AppState.focusPoint == undefined) {
            AppState.hoverTimeout = setTimeout(function () {
                highlightPath(d.id)
            }, 500)
        }

        d3.select(this).style("stroke", "black")
        AppState.hoverpoint = this
    }
}

/**
 *  Event "mouseleave":
 *      - hide the tooltip
 *      - remove the stroke
 *      - clear the path 
 */
export function onMouseLeave() {
    // clear the path only if there is no selection
    if (AppState.focusPoint === undefined) {
        clearPathHighlight()
    }
    else {
        d3.select(this).style("stroke", null)
    }
    if (this !== AppState.focusPoint) {
        hideTooltip(this)
    }
    AppState.hoverpoint = undefined

}

/* -------------------------------------------------------------------------- */
/*                               PATH FUNCTIONS                               */
/* -------------------------------------------------------------------------- */

/**
 *  Highlight the "path" of a node :
 *  -> get all possible targets starting from this node
 *  -> get closest sources
 * 
 * performance hack : use opacity mask
 * so order must be set correctly : 
 * (g) view
 * ├── (path) highlighted nodes 
 * ├── (line) highlighted links
 * ├── (g) hull layer (visible or not)
 * |   ├── (rect) opacity mask for hulls
 * |   └── (path) convex hulls
 * ├── (rect) main opacity mask (visible)
 * ├── (path) others nodes
 * └── (line) others links
 * 
 *  @param {int} id index of the node
 */
export function highlightPath(id) {

    highlightLinksTarget(id)
    highlightLinksSource(id)

    d3.select(".fade-mask").raise().attr("visibility", "visible")
    if (AppState.isHullVisible) {
        d3.select("#hullLayer").raise()
    }
    d3.selectAll(".linkInPath").raise()
    d3.selectAll(".selectInPath, .flag").raise()
}

/**
 * [RECURSIVE] Highlight all possible targets starting from a node.
 * @param {int} id index of the node
 */
function highlightLinksTarget(id) {
    d3.select(`[data-id='node-${id}']`).classed("selectInPath", true)
    const sources = getSourcesLinks(id)
    sources.each(function (l) {
        // ignore recursive function, hidden links & pts
        if (l.target.id !== id && d3.select(this).attr("hidden") == undefined) {
            d3.select(this).classed("linkInPath", true)
            if (d3.select(`[data-id='node-${l.target.id}']`).classed("selectInPath") !== true) {
                highlightLinksTarget(l.target.id)
            }
        }

    }
    )
}


/**
 * Highlight closest sources from a node.
 * @param {int} id index of the node
 */
function highlightLinksSource(id) {
    d3.select(`[data-id='node-${id}']`).classed("selectInPath", true)
    const targets = getTargetLinks(id)
    targets.each(function (l) {
        // ignore hidden links & pts
        if (d3.select(this).attr("hidden") == undefined) {
            d3.select(this).classed("linkInPath", true)
            d3.select(`[data-id='node-${l.source.id}']`).classed("selectInPath", true)
        }
    }
    )
}


/**
 *  Clear any "path" (see HighlightPath function)
 */
export function clearPathHighlight() {
    clearTimeout(AppState.hoverTimeout)
    d3.selectAll(".linkInPath").lower()
    d3.select("#card").attr("hidden", true)
    d3.select(".fade-mask").attr("visibility", "hidden")
    d3.selectAll(`[data-id^='node-']`)
        .classed("selectInPath", false)
        .style("stroke", "white")
    d3.selectAll(".linkline").classed("linkInPath", false)
    AppState.nodeIndexSet = undefined
}

/* -------------------------------------------------------------------------- */
/*                              TOOLTIP FUNCTION                              */
/* -------------------------------------------------------------------------- */

/**
 * Show a node's tooltip.
 * @param {Object} el node (dom)
 */
export function showTooltip(el) {
    const el_index = d3.select(el).attr("index")
    const index = AppState.tooltips.findIndex(item => item.index === el_index)
    if (index > -1) {
        // already existing = show it if not already visible
        if (AppState.tooltips[index].visible === false) {
            thistooltip.show()
            AppState.tooltips[index].visible = true
        }
    }
    else {
        // not existing = create the tooltip
        const thistooltip = new bootstrap.Tooltip(el)
        thistooltip.show()
        AppState.tooltips.push({ index: el_index, el: thistooltip, visible: true })
    }

}

/**
 * Hide (or rather delete) a node's tooltip.
 * @param {Object} el node (dom)
 */
export function hideTooltip(el) {
    // check class
    if (d3.select(el).classed("flag") === false) {
        const el_index = d3.select(el).attr("index")
        const index = AppState.tooltips.findIndex(item => item.index === el_index)
        if (index > -1) { // finds an index
            const thistooltip = AppState.tooltips[index]
            if (thistooltip.visible === true) {
                // delete
                thistooltip.el.dispose()
            }
            AppState.tooltips.splice(index, 1)
        }
    }

}

