/** Update the changelog colors in dark mode */

const changelog = document.getElementById("changelog");

function updateEntryColor(entry) {
    const line = entry.lastChild;
    const lightColorSpan = line.childNodes.item(1);
    const darkColorSpan = lightColorSpan.cloneNode(true);

    line.insertBefore(darkColorSpan, lightColorSpan);

    lightColorSpan.classList.add("light");
    darkColorSpan.classList.add("dark");

    let color;
    switch (darkColorSpan.textContent) {
        case "Feature":
            color = "#5BF38E";
            break;
        case "Support":
            color = "#55A5E7";
            break;
        case "Bug":
            color = "#E14F4F";
            break;
        default:
            color = null;
    }

    darkColorSpan.style["color"] = color;
}

if (changelog !== null) {
    for (let collection of changelog.getElementsByClassName("simple")) {
        Array.from(collection.children).forEach(updateEntryColor);
    }
}
