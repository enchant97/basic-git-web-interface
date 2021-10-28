"use-strict";

function select_navigate_to(element) {
    document.location.assign(element.value);
}

ThemeChanger.theme_meta.light[1] = [
    ["--font-dark", "black"],
    ["--font-light", "#f0f0f0"],
    ["--bg-col", "#c4c4c4"],
    ["--bg-sub-col", "#afafaf"],
    ["--bnt-col", "#666666"],
];
ThemeChanger.theme_meta.dark[1] = [
    ["--font-dark", "var(--font-light)"],
    ["--font-light", "#bebebe"],
    ["--bg-col", "#262626"],
    ["--bg-sub-col", "#202020"],
    ["--bnt-col", "#3d3d3d"],
];
ThemeChanger.theme_picker_parent = document.querySelector("main");

document.getElementById("themeToggleBnt").addEventListener("click", _ => {
    ThemeChanger.toggle_theme_picker();
});

ThemeChanger.on_load();
