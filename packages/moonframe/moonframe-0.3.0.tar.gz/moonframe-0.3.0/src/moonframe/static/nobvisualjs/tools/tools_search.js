import { focusOnElement } from "./tools_zoom.js"
/**
 * Add listeners for the search
 * @param {*} root Packed data
 * @param {*} node Circles data
 */
export function Search(root, node) {
    const searchInput = d3.select("#searchInput")

    // reboot everything
    searchInput.on("click", function () {
        searchInput.attr("class", "form-control")
        d3.select("#errorinfo").remove()
    })
    searchInput.on("keyup", function (event) {
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
            searchElement(event, root, node)
        }
    })
}

/**
 * Search a node on the graph(with the search bar)
* @param { event } event keyup event
* @param { Object } root 
* @param { Object } node 
*/
export function searchElement(event, root, node) {
    const searchInput = d3.select("#searchInput")
    const searchTerm = searchInput.property("value")
    const tablebody = d3.select("#tablebody")
    const table = d3.select(".table-responsive")
    let matches = root.descendants().filter(d => d.nameID.includes(searchTerm))

    if (matches.length !== 0) { // something found

        if (matches.length > 1) { // more than one match -> create a menu
            // show the table
            table.attr("hidden", null)

            // not too much matches
            if (matches.length > 10) {
                matches = matches.slice(0, 10)
            }

            // set the table
            matches.forEach(d => {
                tablebody.append("tr")
                    .append("td")
                    .html(d.data.path)
                    .attr("class", "tabledata")
                    .on("click", function () {
                        // mock click 
                        focusOnElement(d, event, root, node)
                        // reset table
                        tablebody.selectAll("tr").remove()
                        table.attr("hidden", true)
                        searchInput.property("value", "")
                        // unselect searchInput
                        searchInput.node().blur()
                    })
                // // mock MouseEnter and MouseLeave
                // .on("mouseenter", function () {
                //     onMouseEnter.call(el, event, d)
                // })
                // .on("mouseleave", function () {
                //     onMouseLeave.call(el)
                // })
            })
        }
        else { // single match
            focusOnElement(matches[0], event, root, node)
        }

    }
    else { // nothign found -> error message
        // placement
        const searchbar = d3.select("#searchbar")

        searchbar.append("g")
            .html(`Can't find ${searchTerm}.`)
            .style("color", "red")
            .style("font-size", "small")
            .attr("id", "errorinfo")
        searchInput.attr("class", "form-control is-invalid")
    }
}

