const userForm = document.getElementById('userForm');
const modalTitle = document.getElementById('modalTitle');
const passwordHelp = document.getElementById('passwordHelp');
const formPassword = document.getElementById('form_password');
const userModal = document.getElementById('userModal');
const modalInstance = new bootstrap.Modal(userModal);

function syncDeptSelectAll() {
    document.querySelectorAll('.dept-select-all').forEach(deptBox => {
        const dept = deptBox.dataset.dept;
        const children = document.querySelectorAll(`.folder-checkbox[data-dept="${dept}"]`);
        deptBox.checked = children.length > 0 && Array.from(children).every(cb => cb.checked);
    });
}

function openCreateModal() {
    // Read the evaluated Django URL from the form's data attribute
    const createUrl = userForm.getAttribute('data-create-url');
    userForm.action = createUrl;

    modalTitle.textContent = "Register New Identity";
    passwordHelp.style.display = 'none';
    formPassword.required = true;

    userForm.reset();

    document.querySelectorAll('.folder-checkbox').forEach(chk => chk.checked = false);
    document.querySelectorAll('.dept-select-all').forEach(chk => chk.checked = false);

    if (modalInstance) {
        modalInstance.show();
    }
}

function openEditModal(buttonElement) {
    const userId = buttonElement.getAttribute('data-id');
    const username = buttonElement.getAttribute('data-username');
    const departmentId = buttonElement.getAttribute('data-department-id');
    const canAccessOtherDepts = buttonElement.getAttribute('data-can-access-other-depts') === 'true';
    const isAdmin = buttonElement.getAttribute('data-is-admin') === 'true';
    const permittedFoldersRaw = buttonElement.getAttribute('data-permitted-folders');

    const permittedFolders = permittedFoldersRaw ? permittedFoldersRaw.split(',') : [];

    // Build the edit URL from a Django-rendered base (data-edit-url-base="/admin/save-user/0/"),
    // swapping the placeholder id for the real one. Keeps URL construction in Django's hands
    // instead of a hardcoded string that can drift from urls.py.
    const editUrlBase = userForm.getAttribute('data-edit-url-base');
    userForm.action = editUrlBase.replace(/0\/$/, `${userId}/`);

    modalTitle.textContent = "Modify User Constraints: " + username;
    passwordHelp.style.display = 'block';
    formPassword.required = false;

    document.getElementById('form_username').value = username;
    document.getElementById('form_password').value = '';
    document.getElementById('form_department').value = departmentId || '';
    document.getElementById('form_is_admin').checked = isAdmin;
    document.getElementById('form_can_access').checked = canAccessOtherDepts;

    const permittedSet = new Set(permittedFolders);
    document.querySelectorAll('.folder-checkbox').forEach(chk => {
        chk.checked = permittedSet.has(chk.value);
    });
    syncDeptSelectAll();

    if (modalInstance) {
        modalInstance.show();
    }
}

// Department "select all" toggles its child folder checkboxes
document.querySelectorAll('.dept-select-all').forEach(deptBox => {
    deptBox.addEventListener('change', function () {
        const dept = this.dataset.dept;
        document.querySelectorAll(`.folder-checkbox[data-dept="${dept}"]`)
            .forEach(cb => cb.checked = this.checked);
    });
});

// If a user unchecks one folder manually, uncheck the parent "select all"
document.querySelectorAll('.folder-checkbox').forEach(cb => {
    cb.addEventListener('change', function () {
        if (!this.checked) {
            const parentToggle = document.querySelector(`.dept-select-all[data-dept="${this.dataset.dept}"]`);
            if (parentToggle) parentToggle.checked = false;
        }
    });
});

// Live filter by folder name
document.getElementById('folderFilterInput').addEventListener('input', function () {
    const term = this.value.toLowerCase();
    document.querySelectorAll('.folder-row').forEach(row => {
        row.classList.toggle('d-none', !row.dataset.folderName.includes(term));
    });
});