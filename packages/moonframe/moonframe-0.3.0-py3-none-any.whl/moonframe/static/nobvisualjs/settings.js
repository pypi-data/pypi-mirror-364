export const WIDTH = window.innerWidth
export const HEIGHT = window.innerHeight

/**
 * Add subtitle
 * @param {string} text Subtitle text
 */
export function addSubtitle(text) {
    const subtitle = d3.select(".modal-body")
    subtitle.html(text)
}

