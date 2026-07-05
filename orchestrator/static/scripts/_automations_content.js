 function switchSubTab(subTabId) {
        // Toggle the active state for tab buttons
        document.querySelectorAll('.sub-tab-link').forEach(btn => {
            if (btn.getAttribute('data-subtab') === subTabId) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Show/hide the targeted panes
        document.querySelectorAll('.subtab-pane').forEach(pane => {
            if (pane.id === 'subtab-' + subTabId) {
                pane.classList.remove('d-none');
            } else {
                pane.classList.add('d-none');
            }
        });
    }