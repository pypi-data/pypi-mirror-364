import { AppState } from "./global.js"
import { createColorLegend, changeColor } from "./color.js"
import { selectPoint, unfocus } from "./clickevent.js"
import { onMouseEnter, onMouseLeave, highlightPath, showTooltip, hideTooltip, clearPathHighlight } from "./mouseevent.js"
import { searchElement } from "./search.js"
import { createSizeScale, changeSize } from "./size.js"
import { setHulls, updateHulls, showHulls, resetHulls } from "./hulls.js"

let nodes
let link
export async function callgraph(data_path, repo_name) {
    const WWIDTH = window.innerWidth
    const WHEIGHT = window.innerHeight
    const WIDTH = WWIDTH
    const HEIGHT = WHEIGHT
    const symbol = d3.symbol()
    let isDragging = false

    /* -------------------------------------------------------------------------- */
    /*                              DATA MANIPULATION                             */
    /* -------------------------------------------------------------------------- */

    const data = await d3.json(data_path)
    const cselect = d3.select("#cselect")
    const sselect = d3.select("#sselect")
    const log10 = d3.select("#log10_checkbox")
    const seeFiles = d3.select("#seefilescheck")
    const links = data.links.map(d => ({ ...d }))
    // to catch the root and the leaves
    const sources = new Set(links.map(link => link.source))
    const targets = new Set(links.map(link => link.target))
    nodes = data.nodes.map(d => ({ ...d }))
        // remove solitary
        .filter(d => (targets.has(d.id) || sources.has(d.id)))
    const searchInput = d3.select("#searchInput")

    /* -------------------------------------------------------------------------- */
    /*                                  INIT PAGE                                 */
    /* -------------------------------------------------------------------------- */

    // init select for scales
    for (let key of Object.entries(nodes[0])) {
        // ignore "useless" categorical metrics : 
        // = those that have only one category or as many categories as points
        const domain = [... (new Set(nodes.map(d => d[key[0]])))]
        const isNotNum = typeof domain[0] !== "number"
        // list of keys to be removed that pass length filters
        const exclude = ["linestart", "name", "filename"]
        if (!(isNotNum && (domain.length === 1 || domain.length === nodes.length)
            || exclude.includes(key[0]))) {
            cselect.append("option").html(key[0]).attr("value", key[0])
            if (!isNotNum) { // create size select
                sselect.append("option").html(key[0]).attr("value", key[0])
            }
        }
    }
    AppState.cKey = cselect.property("value")
    AppState.sKey = sselect.property("value")
    // create color legend
    createColorLegend(nodes)
    createSizeScale(nodes)

    // repo name
    d3.select("#repo-name").html("The structure of " + repo_name)

    // help card
    d3.select("#help").on("click", function () {
        const modalElement = document.getElementById('helpModal')
        const modalInstance = new bootstrap.Modal(modalElement)
        modalInstance.show()
    })

    /* -------------------------------------------------------------------------- */
    /*                                  INIT SVG                                  */
    /* -------------------------------------------------------------------------- */

    let inposX = []
    let counterX = 1
    let inposY = []
    const nbNodes = nodes.length
    function getOrAssignX(d) {
        if (!inposX[d.filename]) {
            inposX[d.filename] = (WIDTH / nbNodes) * counterX
            counterX++
        }
        return inposX[d.filename]
    }
    function getOrAssignY(d) {
        if (!inposY[d.filename]) {
            inposY[d.filename] = HEIGHT / (Math.random() * (d.filename.length + 1) + 1)
        }
        return inposY[d.filename]
    }
    // create forces
    const simulation = d3.forceSimulation(nodes)
        .on("tick", ticked)
        .force('x', d3.forceX(getOrAssignX))
        .force('y', d3.forceY(getOrAssignY))
        .force("link", d3.forceLink(links).id(d => d.id)
            .strength(function (l) {
                if (l.source.filename === l.target.filename) {
                    // stronger link for links within a group
                    return 2
                }
                else {
                    return 0.01
                }
            }))
        .force("charge", d3.forceManyBody().strength(-600))
        .force("center", d3.forceCenter(WIDTH / 2, HEIGHT / 2))
        .force("collide", d3.forceCollide(17))
    //performances
    simulation.alphaMin(0.005)

    // set svg
    const svg = d3.select("#svg")
        .attr("viewBox", `0 0 ${WIDTH} ${HEIGHT}`)
        .attr("style", "max-width: 100%; height: auto; font: 10px sans-serif;")

    // performance hack : use opacity mask
    // so order is important :
    // svg
    // ├── (g) view
    // |   ├── (path) nodes 
    // |   ├── (line) links
    // |   ├── (g) hull layer (hidden)
    // |   |   ├── (rect) opacity mask for hulls
    // |   |   └── (path) convex hulls
    // |   └── (rect) main opacity mask (hidden)
    // └── (g) foreground
    //     ├── (circle) flags
    //     └── (g) orbit container 
    //         └── (g) orbit group 

    const view = svg.append("g")
    // convex hulls for clustering
    const hullLayer = view.append("g")
        .attr("id", "hullLayer")
    const convexHulls = hullLayer.append("g").attr("class", "hulls")
    setHulls(nodes)
    const maskHull = hullLayer.append("rect")
        .attr("id", "hull-mask")
        .style("opacity", "0.6")
        .style("pointer-events", "none")
        .style("fill", "white")
    // foreground
    const foreground = svg.append("g").attr("id", "foreground")

    // opacity gradient underneath the menu
    const gradient = svg.append("defs")
        .append("linearGradient")
        .attr("id", "fade-gradient")
        .attr("x1", "0%").attr("y1", "0%")
        .attr("x2", "100%").attr("y2", "0%")

    gradient.append("stop")
        .attr("offset", "0%")
        .attr("stop-color", "white")
        .attr("stop-opacity", 1)

    gradient.append("stop")
        .attr("offset", "100%")
        .attr("stop-color", "white")
        .attr("stop-opacity", 0)

    svg.append("rect")
        .attr("id", "mask")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", "400px")
        .attr("height", HEIGHT)
        .attr("fill", "url(#fade-gradient)")

    const mask = view.append("rect")
        .attr("class", "fade-mask")
        .style("opacity", "0.9")
        .style("pointer-events", "none")
        .style("fill", "white")
        .attr("visibility", "hidden")

    // set zoom
    const zoom = d3.zoom()
        .on("zoom", (event) => {
            const t = event.transform
            view.attr("transform", t)
            foreground.attr("transform", t)

            const topLeft = t.invert([0, 0])
            const bottomRight = t.invert([window.innerWidth, window.innerHeight])

            const x = topLeft[0]
            const y = topLeft[1]
            const width = bottomRight[0] - x
            const height = bottomRight[1] - y

            mask
                .attr("x", x)
                .attr("y", y)
                .attr("width", width)
                .attr("height", height)
            maskHull
                .attr("x", x)
                .attr("y", y)
                .attr("width", width)
                .attr("height", height)


            AppState.tooltips.forEach(obj => obj.el.update())
            if (AppState.groupTooltip !== undefined) {
                AppState.groupTooltip.update()
            }
        })
    svg.call(zoom)
    // set first view
    svg.call(zoom.transform, d3.zoomIdentity.scale(0.2).translate(WIDTH / 0.5, HEIGHT / 0.5))

    // set links
    link = view
        .selectAll()
        .data(links)
        .join("line")
        .attr("class", "linkline")
        .attr("stroke", d => AppState.color(d.source[AppState.cKey]))
        .attr("data-id", d => `link-${d.source.id}`)
        .attr("marker-end", (d, i) => setArrow(AppState.color(d.source[AppState.cKey]), AppState.size(d.target[AppState.sKey]), i))

    // set nodes
    const node = view
        .selectAll()
        .data(nodes)
        .join("path")
        .attr("stroke", "#fff")
        .attr("stroke-width", 2)
        // different symbols
        .attr("d", d => {
            if (!targets.has(d.id)) return symbol.type(d3.symbolStar).size(AppState.size(d[AppState.sKey]))()
            if (!sources.has(d.id)) return symbol.type(d3.symbolSquare).size(AppState.size(d[AppState.sKey]))()
            return symbol.type(d3.symbolCircle).size(AppState.size(d[AppState.sKey]))() // default
        })
        .attr("fill", d => AppState.color(d[AppState.cKey]))
        .style("--fill-color", d => AppState.color(d[AppState.cKey]))
        .attr("data-id", d => `node-${d.id}`)
        .attr("index", (_, i) => i)
        // tooltip
        .attr("data-bs-toggle", "tooltip")
        .attr("data-bs-title", d => d.name)
        .attr("data-bs-trigger", "manual")
        // custom classes
        .classed("flag", false)
        .classed("selectInPath", false)
        .classed("select", false)
        // events
        .on("click", function (event, d) {
            selectPoint(this, d)
        })
        .on("mouseenter", onMouseEnter)
        .on("mouseleave", onMouseLeave)

    mask.raise()

    // set moving dots (at selection)
    const orbit = foreground.append("g")
        .attr("class", "orbit-container")
    const orbitgroup = orbit.append("g").attr("class", "orbit-group")

    /* -------------------------------------------------------------------------- */
    /*                                  LISTENERS                                 */
    /* -------------------------------------------------------------------------- */

    // reboot 
    svg.on("click", function (event) {
        const table = d3.select(".table-responsive")
        // click on the background :
        if (event.target == svg.node() && AppState.focusPoint !== undefined) {
            unfocus()
        }
        // click anywhere on the svg (background+elements)
        // reboot seach
        d3.select("#searchInput").property("value", "")
            .attr("class", "form-control")
        d3.select("#tablebody").selectAll("tr").remove()
        table.attr("hidden", true)
        d3.select("#errorinfo").remove()
    })

    // drag
    node.call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    // color related
    cselect.on("change", function (event) {
        AppState.cKey = this.value
        changeColor(nodes)
        cselect.node().blur()
    })
    log10.on("change", function () {
        AppState.isLog = !AppState.isLog
        changeColor(nodes)
    })

    // see files
    seeFiles.on("change", function () {
        AppState.isHullVisible = !AppState.isHullVisible
        // don't show convex hulls
        if (!AppState.isHullVisible) {
            // set color to default
            cselect.select("#filenames").remove()
            AppState.cKey = cselect.property("value")
            changeColor(nodes)
            cselect.attr("disabled", null)
            log10.attr("disabled", null)
            // hide hulls + mask hull
            resetHulls()
            d3.select(".hulls").selectAll("*").attr("visibility", "hidden")
            d3.select("#hull-mask").attr("visibility", "hidden")
            // reset fade-mask opacity
            d3.select(".fade-mask").style("opacity", "0.9")
        }
        // show convex hulls
        else {
            // set color to filename
            cselect.append("option").html("filenames").attr("value", "filenames").attr("id", "filenames")
            cselect.property("value", "filenames")
            AppState.cKey = "filename"
            changeColor(nodes)
            // then disable color change
            cselect.attr("disabled", true)
            log10.attr("disabled", true)
            // show hulls
            showHulls(nodes)
            // change fade-mask opacity
            d3.select(".fade-mask").style("opacity", "0.3")
        }
    })

    // size
    sselect.on("change", function () {
        AppState.sKey = this.value
        changeSize(nodes, targets, sources)
    })

    // search
    searchInput.on("click", function () {
        // reboot
        searchInput.attr("class", "form-control")
        d3.select("#errorinfo").remove()
    })

    // keyboard (on search bar)
    searchInput.on('keyup', function (event) {
        // reboot
        searchInput.attr("class", "form-control")
        d3.select("#tablebody").selectAll("tr").remove()
        d3.select("#errorinfo").remove()

        // user deletes their input
        if (event.key == "Backspace" && searchInput.property("value") === "") {
            d3.select(".table-responsive").attr("hidden", true)
        }
        // else : search
        else {
            searchElement(event, nodes)
        }
    })

    // keyboard (general)
    document.addEventListener("keydown", function (event) {
        // hide point on "h"
        if (event.key == "h") {
            if (AppState.hoverpoint != undefined) {
                const domPoint = d3.select(AppState.hoverpoint)
                const id = domPoint.attr("data-id").split("-")[1]
                const index = domPoint.attr("index")

                hideTooltip(AppState.hoverpoint)

                domPoint.attr("hidden", true)

                // hide parent links
                const sources = link.filter(l => l.target.id === id)
                sources.each(function (l) {
                    d3.select(this).attr("hidden", true)
                    const index = this.getAttribute("index")
                })
                // hide children links
                const target = link.filter(l => l.source.id === id)
                target.each(function (l) {
                    d3.select(this).attr("hidden", true)
                    const index = this.getAttribute("index")
                })
                // special handle for the flags
                if (domPoint.classed("flag") == true) {
                    domPoint.classed("flag", false)
                    svg.selectAll(`[id^='circle-flag-']`).remove()
                }
                resetHulls()
                // special handle when there is a focusPoint
                if (AppState.focusPoint !== undefined) {
                    // if the point is a focusPoint : unfocus it
                    if (AppState.hoverpoint == AppState.focusPoint) {
                        unfocus()
                    }
                    // if the point was in the selected point path : recreate path
                    // = ignore the children of the hidden point
                    else if (d3.select(AppState.hoverpoint).classed("selectInPath") == true) {
                        const id_focus = d3.select(AppState.focusPoint).attr("data-id").split("-")[1]
                        d3.selectAll(".linkline").classed("linkInPath", false)
                        d3.selectAll(`[data-id^='node-']`).classed("selectInPath", false)
                            .style("stroke", null)
                        highlightPath(id_focus)
                    }
                    // else... nothing change
                    // but in practice, "else" case never happens because 
                    // the hover event is limited to points in the path
                }
                AppState.hoverpoint = undefined
            }
        }
        // hide point on "f"
        else if (event.key == "f") {
            if (AppState.hoverpoint) {
                d3.select(AppState.hoverpoint).style("stroke", null)
                const domPoint = d3.select(AppState.hoverpoint)
                const index = domPoint.attr("index")
                const data = nodes[index]
                // set flag
                if (domPoint.classed("flag") === false) {
                    domPoint.classed("flag", true)
                    showTooltip(AppState.hoverpoint)
                    foreground.append("circle")
                        .attr("id", `circle-flag-${index}`)
                        .attr("r", Math.sqrt(AppState.size(data[AppState.sKey])) + 2)
                        .style("fill", AppState.color(data[AppState.cKey]))
                        .style("stroke", AppState.color(data[AppState.cKey]))
                        .attr("cx", data.x)
                        .attr("cy", data.y)
                        .attr("opacity", "0.3")
                        .style("pointer-events", "none")
                        .lower()
                }
                // delete flag
                else {
                    domPoint.classed("flag", false)
                    svg.select(`#circle-flag-${index}`).remove()
                }
            }
        }
        // remove all flags
        else if (event.key == "F" && event.shiftKey) {
            d3.selectAll(`[data-id^='node-']`).classed("flag", false)
            AppState.tooltips.forEach(obj => obj.el.hide())
            AppState.tooltips = []
            svg.selectAll(`[id^='circle-flag-']`).remove()
        }
        // show all points on "shift+h" or... "H" 
        else if (event.key == "H" && event.shiftKey) {
            d3.selectAll(`[data-id^='node-']`).attr("hidden", null)
            d3.selectAll("line").attr("hidden", null)
            if (AppState.focusPoint !== undefined) {
                const id_focus = d3.select(AppState.focusPoint).attr("data-id").split("-")[1]
                highlightPath(id_focus)
            }
        }
    })


    d3.select("#zoomIn").on("click", function () {
        const currentZoom = d3.zoomTransform(svg.node())
        svg.transition().duration(300)
            .call(zoom.transform, d3.zoomIdentity
                .scale(currentZoom.k * 1.5)
                .translate(WIDTH, HEIGHT)
            )
    })


    /* -------------------------------------------------------------------------- */
    /*                                 SIMULATION                                 */
    /* -------------------------------------------------------------------------- */


    /**
     *  Is called each time the simulation ticks : update position of all elements 
     */
    function ticked() {

        // centroids 
        let alpha = this.alpha()
        let centroids = {}
        let coords = {}
        let groups = []

        // sort the nodes into groups:  
        node.each(function (d) {
            if (groups.indexOf(d.filename) == -1) {
                groups.push(d.filename)
                coords[d.filename] = { x: d.x, y: d.y, n: 1 }
            }
            else {
                coords[d.filename].x += d.x
                coords[d.filename].y += d.y
                coords[d.filename].n += 1
            }
        })

        for (let group in coords) {
            let groupNodes = coords[group]
            let cx = groupNodes.x / groupNodes.n
            let cy = groupNodes.y / groupNodes.n

            centroids[group] = { x: cx, y: cy }
        }

        // adjust each point if needed towards group centroid:
        node.each(function (d) {
            let cx = centroids[d.filename].x
            let cy = centroids[d.filename].y

            d.vx -= (d.x - cx) * 0.1 * alpha
            d.vy -= (d.y - cy) * 0.1 * alpha
        })

        node
            .attr("transform", d => `translate(${d.x},${d.y})`)

        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            // shorten links so that they end at the node boundary
            .attr("x2", d => {
                const dx = d.target.x - d.source.x
                const dy = d.target.y - d.source.y
                const len = Math.sqrt(dx * dx + dy * dy)
                const r = Math.sqrt(AppState.size(d.target[AppState.sKey]) / Math.PI)
                return len === 0 ? d.target.x : d.target.x - (dx / len) * r
            })
            .attr("y2", d => {
                const dx = d.target.x - d.source.x
                const dy = d.target.y - d.source.y
                const len = Math.sqrt(dx * dx + dy * dy)
                const r = Math.sqrt(AppState.size(d.target[AppState.sKey]) / Math.PI)
                return len === 0 ? d.target.y : d.target.y - (dy / len) * r
            })

        // orbit
        if (AppState.focusPoint !== undefined) {
            const d = nodes[d3.select(AppState.focusPoint).attr("index")]
            orbit.attr("transform", `translate(${d.x},${d.y})`)
        }

        // tooltip(s)
        AppState.tooltips.forEach(function (obj) {
            obj.el.update()
        })
        if (AppState.groupTooltip !== undefined) {
            AppState.groupTooltip.update()
        }

        // circle-flag
        svg.selectAll(".flag").each(function () {
            const index = d3.select(this).attr("index")
            const data = nodes[index]
            const circle = d3.select(`#circle-flag-${index}`)
                .attr("cx", data.x)
                .attr("cy", data.y)
        }

        )

        // convex hulls
        if (AppState.isHullVisible) {
            updateHulls(nodes)
        }
    }


    /**
     * Is called when drag starts
     * @param {event} event 
     * @param {Object} d 
     */
    function dragstarted(event, d) {
        AppState.isItADrag = true
        isDragging = true
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }

    /**
     * Update the subject (dragged node) position during drag.
     * @param {event} event 
     */
    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }

    /**
     * Is called at the end of drag
     * @param {*} event 
     * @param {*} d 
     */
    function dragended(event, d) {
        AppState.isItADrag = false
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }

    return svg.node();
}

/* -------------------------------------------------------------------------- */
/*                              EXPORT FUNCTIONS                              */
/* -------------------------------------------------------------------------- */

/**
 * Get the data of a node
 * @param {Object} el node 
 * @returns data
 */
export function get_data(el) {
    const index = d3.select(el).attr("index")
    return nodes[index]
}

/**
 * Get the data of multiple nodes
 * @param {Object} el nodes 
 * @returns data
 */
export function get_multiple_data(el) {
    const indexes = [...d3.selectAll(el).attr("index")]
    return nodes.filter((el, i) => indexes.includes(`${i}`))
}

// maybe not ideal this part but... 

/**
 * Get all the links with "id" as source
 * @param {int} id Index of a node
 * @returns Links with "id" as source
 */
export function getSourcesLinks(id) {
    return link.filter(l => l.source.id === id)
}

/**
 * Get all the links with "id" as target
 * @param {int} id Index of a node
 * @returns Links with "id" as target
 */
export function getTargetLinks(id) {
    return link.filter(l => l.target.id === id)
}


/**
* Set the arrows at the end of the lines
* @param {Object} color color scale
* @returns 
*/
export function setArrow(color, size, icol) {
    const svg = d3.select("#svg")

    // reset if needed
    const lastArrow = svg.select(`#arrowhead-${icol}`)
    if (!lastArrow.empty()) {
        lastArrow.node().parentNode.remove()
    }
    const realSize = Math.sqrt(size / Math.PI) + 2
    const arrowSize = Math.trunc(realSize / 3)
    svg.append("defs").append("marker")
        .attr("id", `arrowhead-${icol}`)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", arrowSize)
        .attr("refY", 0)
        .attr("markerWidth", arrowSize)
        .attr("markerHeight", arrowSize)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5")
        .attr("fill", color)

    return `url(#arrowhead-${icol})`;
}