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

// Theme picker setup
ThemeChanger.theme_picker_parent = document.querySelector("main");
ThemeChanger.use_local = true;
ThemeChanger.selected_theme_css_class = "current";
const themeToggleBnt = document.getElementById("themeToggleBnt");
themeToggleBnt.addEventListener("click", ThemeChanger.toggle_theme_picker);
themeToggleBnt.classList.remove("hidden");
ThemeChanger.on_load();

// Setup removing expired "flashes"
document.querySelectorAll("[data-dismiss='flash']").forEach(element => {
    setTimeout(() => { element.remove() }, 4000);
});
