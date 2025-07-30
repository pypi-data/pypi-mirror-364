import { view } from "./tools_zoom.js"
import { isTransition } from "./tools_zoom.js"
import { HEIGHT, WIDTH } from "../settings.js"
import { onFocus } from "./tools_zoom.js"

/**
 * [recursive] call circularText only when zoom transition is complete.
 * @param {*} d Selected circle
 * @param {*} node Circle data
 */
export function callTextAfterZoom(d, node) {
    if (isTransition) { // waiting for zoom transition to end
        setTimeout(() => { callTextAfterZoom(d, node) }, 50)
    }
    else {
        // if during the transition another node is selected -> don't call circularText
        // > don't know the focus has changed because it's based on "isTransition" not the transition itself.
        // > there isn't a built in way to check the status of the transition 
        if (d === onFocus) {
            if (!d.parent) { // root
                node.each(function (d) {
                    circularText(d)
                })
            }
            else {
                if (d.children) {
                    for (const child of d.children) {
                        circularText(child, [WIDTH / 2 - view[0], HEIGHT / 2 - view[1]])
                    }
                }
                circularText(d, [WIDTH / 2 - view[0], HEIGHT / 2 - view[1]])
            }
        }

    }
}

/**
* Draw the name/title of the circle following its circumference.
* @param {*} d Selected circle
* @param {Array} delta (Optional) translation (x,y). Default to [0, 0]
*/
export function circularText(d, delta = [0, 0]) {
    const k = HEIGHT / view[2]
    const r = d.r * k
    const cx = (d.x - WIDTH / 2 + delta[0]) * k
    const cy = (d.y - HEIGHT / 2 + delta[1]) * k
    const text = d.nameID
    const col = d.colorID
    const svg = d3.select("#main").append("g").attr("class", "circularText")

    const path = svg.append("path")
        .attr("id", `circlePath-${d.ID}`)
        .attr("d", `M ${cx}, ${cy + r}
                A ${r},${r} 0 1,1 ${cx}, ${cy - r}
                A ${r},${r} 0 1,1 ${cx}, ${cy + r}`)
        .attr("fill", "none")

    const textElement = svg.append("text")
        .attr("text-anchor", "middle")
        .attr("stroke", "white")
        .attr("stroke-width", 3)
        .attr("paint-order", "stroke")
        .attr("letter-spacing", "1.05px")
        .style("font-size", `15px`)
        .style("fill", `${col}`)
        .append("textPath")
        .attr("startOffset", "50%")
        .attr("id", `circleText-${d.ID}`)
        .attr("href", `#circlePath-${d.ID}`)
        .text(text)

    //if the text is too big compared to the circle -> remove
    if (textElement.node().parentNode.getComputedTextLength() >= (2 * Math.PI * r) * 0.6
        || textElement.node().getBBox().height > r) {
        svg.remove()
    }

}
