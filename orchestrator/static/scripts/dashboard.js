document.addEventListener("DOMContentLoaded", function () {
    const tabLinks = document.querySelectorAll(".nav-link-tab");
    const tabContents = document.querySelectorAll(".tab-pane-content");
    const projectsSection = document.getElementById("sidebar-projects-section");

    tabLinks.forEach(link => {
        link.addEventListener("click", function (e) {
            e.preventDefault();

            // 1. Clear active classes from all tab links
            tabLinks.forEach(item => item.classList.remove("active"));
            
            // 2. Set current link as active
            this.classList.add("active");

            // 3. Hide all workspace views
            tabContents.forEach(content => content.classList.add("d-none"));

            // 4. Reveal target workspace panel
            const selectedTab = this.getAttribute("data-tab");
            const targetContent = document.getElementById(`tab-content-${selectedTab}`);
            if (targetContent) {
                targetContent.classList.remove("d-none");
            }

            // 5. Context-aware sidebar behavior: Toggle project section visibility
            if (selectedTab === "automation") {
                projectsSection.classList.remove("d-none");
            } else {
                projectsSection.classList.add("d-none");
            }
        });
    });
});