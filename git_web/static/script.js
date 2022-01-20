"use-strict";

function select_navigate_to(element) {
    document.location.assign(element.value);
}

async function copy_to_clipboard(text) {
    let result = await navigator.permissions.query({ name: "clipboard-write" });
    if (result.state == "granted" || result.state == "prompt") {
        await navigator.clipboard.writeText(text);
    }
}

// Setup site theme
ThemeChanger.theme_meta.light[1] = [
    ["--font-dark", "black"],
    ["--font-light", "#f0f0f0"],
    ["--bg-col", "#c4c4c4"],
    ["--bg-sub-col", "#cbcbcb"],
    ["--bnt-col", "#666666"],
];
ThemeChanger.theme_meta.dark[1] = [
    ["--font-dark", "var(--font-light)"],
    ["--font-light", "#bebebe"],
    ["--bg-col", "#262626"],
    ["--bg-sub-col", "#242424"],
    ["--bnt-col", "#3d3d3d"],
];
ThemeChanger.theme_picker_parent = document.querySelector("main");

document.getElementById("themeToggleBnt").addEventListener("click", _ => {
    ThemeChanger.toggle_theme_picker();
});

ThemeChanger.on_load();

// Setup removing expired "flashes"
document.querySelectorAll("[data-dismiss='flash']").forEach(element => {
    setTimeout(() => { element.remove() }, 4000);
});
