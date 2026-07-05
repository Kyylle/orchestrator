document.addEventListener("DOMContentLoaded", function () {

    const sidebar = document.getElementById("sidebarContainer");
    const toggleBtn = document.getElementById("sidebarToggle");
    const toggleIcon = document.getElementById("toggleIcon");

    const tabLinks = document.querySelectorAll(".nav-link-tab");
    const tabContents = document.querySelectorAll(".tab-pane-content");
    const scrollContainer = document.querySelector(".dynamic-scroll-container");

    /* =========================================================
       INIT: RESTORE SIDEBAR STATE
    ========================================================= */
    const savedState = localStorage.getItem("sidebar-collapsed");

    if (savedState === "true" && sidebar) {
        sidebar.classList.add("sidebar-collapsed");
        if (toggleIcon) toggleIcon.style.transform = "rotate(180deg)";
    }

    /* =========================================================
       SIDEBAR TOGGLE
    ========================================================= */
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener("click", function () {

            sidebar.classList.toggle("sidebar-collapsed");

            const isCollapsed = sidebar.classList.contains("sidebar-collapsed");

            localStorage.setItem("sidebar-collapsed", isCollapsed);

            if (toggleIcon) {
                toggleIcon.style.transition = "transform 0.2s ease";
                toggleIcon.style.transform = isCollapsed
                    ? "rotate(180deg)"
                    : "rotate(0deg)";
            }
        });
    }

    /* =========================================================
       TAB SYSTEM
    ========================================================= */
    function activateTab(tabName) {

        if (!tabName) return;

        // reset scroll (important for UX)
        if (scrollContainer) {
            scrollContainer.scrollTop = 0;
        }

        // hide all tabs
        tabContents.forEach(content => {
            content.classList.add("d-none");
        });

        // show selected tab
        const target = document.getElementById(`tab-content-${tabName}`);

        if (!target) {
            console.warn("Tab not found:", tabName);
            return;
        }

        target.classList.remove("d-none");

        // update sidebar active state
        tabLinks.forEach(link => {
            const linkTab = link.dataset.tab;
            link.classList.toggle("active", linkTab === tabName);
        });
    }

    /* =========================================================
       CLICK HANDLER
    ========================================================= */
    tabLinks.forEach(link => {
        link.addEventListener("click", function (e) {
            e.preventDefault();

            const tab = this.dataset.tab;
            if (!tab) return;

            activateTab(tab);

            // update URL hash
            window.history.replaceState(null, "", `#${tab}`);
        });
    });

    /* =========================================================
       LOAD TAB FROM URL HASH
    ========================================================= */
    function getInitialTab() {
        const hash = window.location.hash.replace("#", "");
        return hash || "home";
    }

    activateTab(getInitialTab());

    /* =========================================================
       HANDLE BACK/FORWARD NAVIGATION
    ========================================================= */
    window.addEventListener("hashchange", function () {
        const hash = window.location.hash.replace("#", "");
        activateTab(hash || "home");
    });

});