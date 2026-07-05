document.addEventListener("DOMContentLoaded", function () {
    const tabLinks = document.querySelectorAll(".nav-link-tab");
    const tabContents = document.querySelectorAll(".tab-pane-content");
    const projectsSection = document.getElementById("sidebar-projects-section");
    
    // Target your admin view container wrap matching base.html configuration
    const adminContainer = document.querySelector(".main-content-panel > .dynamic-scroll-container:has(> .admin-user-management)");

    tabLinks.forEach(link => {
        link.addEventListener("click", function (e) {
            e.preventDefault();

            // Toggle selected navigation states
            tabLinks.forEach(item => item.classList.remove("active"));
            this.classList.add("active");

            // Hide standard content tabs
            tabContents.forEach(content => content.classList.add("d-none"));

            const selectedTab = this.getAttribute("data-tab");

            if (selectedTab === "user_management") {
                // Show Admin Panels, hide baseline tabs
                if (adminContainer) adminContainer.classList.remove("d-none");
                projectsSection.classList.add("d-none");
            } else {
                // Return to baseline views layout routing
                if (adminContainer) adminContainer.classList.add("d-none");
                
                const targetContent = document.getElementById(`tab-content-${selectedTab}`);
                if (targetContent) targetContent.classList.remove("d-none");

                // Toggle dynamic secondary folders drawer
                if (selectedTab === "automation") {
                    projectsSection.classList.remove("d-none");
                } else {
                    projectsSection.classList.add("d-none");
                }
            }
        });
    });
});
