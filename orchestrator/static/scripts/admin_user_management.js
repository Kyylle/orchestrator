const userForm = document.getElementById('userForm');
const modalTitle = document.getElementById('modalTitle');
const passwordHelp = document.getElementById('passwordHelp');
const formPassword = document.getElementById('form_password');

function openCreateModal() {
    // Read the evaluated Django URL from the form's data attribute
    const createUrl = userForm.getAttribute('data-create-url');
    userForm.action = createUrl; 

    modalTitle.textContent = "Register New Identity";
    passwordHelp.style.display = 'none';
    formPassword.required = true;

    userForm.reset();
    
    document.querySelectorAll('.folder-checkbox').forEach(chk => chk.checked = false);

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

    // Use an absolute root-relative path (starting with /) so it resolves correctly
    userForm.action = "/admin/save-user/" + userId + "/";
    
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

    if (modalInstance) {
        modalInstance.show();
    }
}

function closeModal() {
    userModal.classList.add('hidden');
}