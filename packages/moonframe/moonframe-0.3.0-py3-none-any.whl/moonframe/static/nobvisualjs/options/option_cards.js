
/**
 * Create a card to show more information.
 * @param {*} root Packed data.
 * @param {*} d Selected circle.
 * @param {string} nameKey Key in the data for the name of the circles
 * @param {string} colorKey Key in the data for the color scale.
 * @param {boolean} worstIsBiggest Worst performers are the biggest (True) or the smallest (False)
 */
export function createCard(root, d, nameKey, colorKey, worstIsBiggest) {
    // option to add a card
    const cardbodyZone = d3.select("#cardbody")
    const card = d3.select("#card")
    const exclude = [nameKey, "children"]
    // reset card
    const cardbody = cardbodyZone.html("").append("div").style("margin-top", "-10px")

    for (let key of Object.entries(d.data)) {
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
        card.style("visibility", "visible")
            .select("#cardheader")
            .html(`${d.nameID}`)
            .style("background-color", d.colorID)
            .style("color", "white")
    }
}