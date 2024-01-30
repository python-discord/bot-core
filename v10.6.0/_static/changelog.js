/** Update the changelog colors in dark mode */
function changelog_color_main() {
    const changelog = document.getElementById("changelog");

    function updateEntryColor(span) {
        const lightColorSpan = span;
        const darkColorSpan = lightColorSpan.cloneNode(true);

        lightColorSpan.parentElement.insertBefore(darkColorSpan, lightColorSpan);

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
                color = lightColorSpan.style.color;
        }

        darkColorSpan.style["color"] = color;
    }

    const TYPES = ["Feature", "Bug", "Support", "Breaking"];

    if (changelog !== null) {
        Array.from(changelog.getElementsByTagName("span"))
            .filter(value => TYPES.includes(value.textContent))
            .forEach(updateEntryColor)
    }
}

changelog_color_main();
