/**
 * Pastry Shop — Interactive Staff Contacts Directory (LR3 Task 3)
 *
 * Implements:
 * 1. Asynchronous staff data loading from database via /contacts/api/.
 * 2. Preloader usage (LR2 infinity preloader) during loading and operations.
 * 3. Column sorting (ascending / descending with graphical arrow indicators).
 * 4. Client-side pagination (maximum 3 items per page) with page controls.
 * 5. Checkbox selection with state preservation across pagination.
 * 6. Live search / filter with "Search" and "Reset" buttons.
 * 7. Row click display of detailed employee information in a card below the table.
 * 8. Add employee form with real-time validation (URL and Phone) and database persistence.
 *    - Invalid fields get red border and pink background.
 *    - Validation message generated below form.
 *    - Submit button activates only when all inputs are valid.
 * 9. Bonus decree generation with selected employees' surnames displayed below table.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if the admin contacts manager is present on the page
    const container = document.getElementById('contacts-admin-container');
    if (!container) return;

    // --- DOM Elements ---
    const preloader = document.getElementById('contacts-preloader');
    const tableBody = document.getElementById('contacts-table-body');
    const tableHeaders = document.querySelectorAll('#contacts-table th.sortable');
    const selectAllCheckbox = document.getElementById('select-all-checkbox');
    const paginationControls = document.getElementById('contacts-pagination');
    const searchInput = document.getElementById('contacts-search-input');
    const searchBtn = document.getElementById('contacts-search-btn');
    const resetBtn = document.getElementById('contacts-reset-btn');
    const toggleAddFormBtn = document.getElementById('toggle-add-employee-btn');
    const addFormPanel = document.getElementById('add-employee-panel');
    const addEmployeeForm = document.getElementById('add-employee-form');
    const submitAddBtn = document.getElementById('submit-add-employee-btn');
    const validationFeedback = document.getElementById('validation-feedback');
    const employeeDetailsCard = document.getElementById('selected-employee-details');
    const awardBonusBtn = document.getElementById('award-bonus-btn');
    const bonusAnnouncementCard = document.getElementById('bonus-announcement-card');

    // Form Inputs
    const inputFirstName = document.getElementById('new-emp-firstname');
    const inputLastName = document.getElementById('new-emp-lastname');
    const inputPosition = document.getElementById('new-emp-position');
    const inputPhone = document.getElementById('new-emp-phone');
    const inputEmail = document.getElementById('new-emp-email');
    const inputDob = document.getElementById('new-emp-dob');
    const inputUrl = document.getElementById('new-emp-url');
    const inputPhoto = document.getElementById('new-emp-photo');

    // --- Application State ---
    let allStaff = [];
    let filteredStaff = [];
    const selectedEmployeeIds = new Set();
    let currentPage = 1;
    const pageSize = 3; // Maximum 3 items per page per requirements
    let currentSort = { field: null, direction: 'asc' };
    let selectedEmployeeIdForDetails = null;

    // --- Validation Rules ---
    /**
     * URL Validation:
     * Must start with http:// or https:// and end with .php or .html
     * Valid example: http://site.ru/index.php, https://example.com/page.html
     * Invalid example: http://site.com, site.ru/index.php
     */
    function validateUrl(url) {
        if (!url || typeof url !== 'string') {
            return { isValid: false, message: 'URL cannot be empty.' };
        }
        const trimmed = url.trim();
        const urlPattern = /^https?:\/\/.+\.(php|html)$/i;
        if (!urlPattern.test(trimmed)) {
            return {
                isValid: false,
                message: 'URL must start with http:// or https:// and end with .php or .html (e.g. http://site.ru/index.php).'
            };
        }
        return { isValid: true, message: 'URL is valid.' };
    }

    /**
     * Phone Number Validation:
     * Starts with +375 or 8.
     * Operator code can be in parentheses or without, with or without spaces.
     * Remaining part may contain hyphens and spaces.
     * Valid examples: 80291112233, 8 (029) 1112233, +375 (29) 111-22-33, +375 (29) 111 22 33
     */
    function validatePhone(phone) {
        if (!phone || typeof phone !== 'string') {
            return { isValid: false, message: 'Phone number cannot be empty.' };
        }
        const trimmed = phone.trim();
        const phonePattern = /^(?:\+375|8)\s*\(?\d{2}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}$/;
        if (!phonePattern.test(trimmed)) {
            return {
                isValid: false,
                message: 'Phone must start with +375 or 8, followed by a valid 2-digit operator code and 7 digits (e.g. +375 (29) 111-22-33 or 80291112233).'
            };
        }
        return { isValid: true, message: 'Phone number is valid.' };
    }

    // --- Preloader Helpers ---
    function showPreloader(message = 'Processing request...') {
        if (preloader) {
            const textEl = preloader.querySelector('.preloader-text');
            if (textEl) textEl.textContent = message;
            preloader.style.display = 'flex';
        }
    }

    function hidePreloader() {
        if (preloader) {
            preloader.style.display = 'none';
        }
    }

    // --- Fetch Staff Data from Database ---
    async function fetchStaffData() {
        showPreloader('Loading staff directory from database...');
        try {
            const response = await fetch('/contacts/api/');
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
            }
            const data = await response.json();
            if (data.status === 'ok' && Array.isArray(data.staff)) {
                allStaff = data.staff;
                filteredStaff = [...allStaff];
                currentPage = 1;
                renderTable();
            } else {
                showNotification('Failed to parse staff data from server.', 'error');
            }
        } catch (err) {
            console.error('Error fetching staff records:', err);
            showNotification('Unable to connect to the staff directory service.', 'error');
        } finally {
            hidePreloader();
        }
    }

    // --- Rendering the Table ---
    function renderTable() {
        tableBody.innerHTML = '';

        if (filteredStaff.length === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td colspan="7" class="text-center no-data">No staff members found matching your criteria.</td>`;
            tableBody.appendChild(tr);
            renderPagination(0);
            updateSelectAllCheckboxState();
            return;
        }

        const totalItems = filteredStaff.length;
        const totalPages = Math.ceil(totalItems / pageSize) || 1;
        if (currentPage > totalPages) currentPage = totalPages;
        if (currentPage < 1) currentPage = 1;

        const startIndex = (currentPage - 1) * pageSize;
        const pageItems = filteredStaff.slice(startIndex, startIndex + pageSize);

        pageItems.forEach((employee) => {
            const tr = document.createElement('tr');
            tr.dataset.id = employee.id;
            tr.classList.add('staff-row');
            if (selectedEmployeeIdForDetails === employee.id) {
                tr.classList.add('active-row');
            }

            const isChecked = selectedEmployeeIds.has(employee.id);

            // Default avatar if no photo exists
            const photoSrc = employee.photo_url || '/static/images/default_avatar.svg';

            tr.innerHTML = `
                <td class="col-checkbox text-center" onclick="event.stopPropagation()">
                    <input type="checkbox"
                           class="emp-checkbox"
                           data-id="${employee.id}"
                           ${isChecked ? 'checked' : ''}
                           aria-label="Select ${escapeHtml(employee.full_name)}" />
                </td>
                <td class="col-photo text-center">
                    <img src="${escapeHtml(photoSrc)}"
                         alt="${escapeHtml(employee.full_name)}"
                         class="staff-table-thumb"
                         onerror="this.src='/static/images/certificate_watermark.svg'" />
                </td>
                <td class="col-name font-semibold">${escapeHtml(employee.full_name)}</td>
                <td class="col-position">${escapeHtml(employee.position)}</td>
                <td class="col-phone font-mono">${escapeHtml(employee.phone)}</td>
                <td class="col-email">
                    <a href="mailto:${escapeHtml(employee.email)}" onclick="event.stopPropagation()">${escapeHtml(employee.email)}</a>
                </td>
                <td class="col-url">
                    ${employee.url
                        ? `<a href="${escapeHtml(employee.url)}" target="_blank" rel="noopener noreferrer" class="emp-web-link" onclick="event.stopPropagation()">View Profile &rarr;</a>`
                        : '<span class="text-muted">—</span>'}
                </td>
            `;

            // Row click: displays employee details below table
            tr.addEventListener('click', (e) => {
                if (e.target.tagName.toLowerCase() === 'input' || e.target.tagName.toLowerCase() === 'a') {
                    return;
                }
                showEmployeeDetails(employee);
            });

            // Individual checkbox click: toggle selection with pagination persistence
            const rowCheckbox = tr.querySelector('.emp-checkbox');
            rowCheckbox.addEventListener('change', (e) => {
                const empId = parseInt(e.target.dataset.id, 10);
                if (e.target.checked) {
                    selectedEmployeeIds.add(empId);
                } else {
                    selectedEmployeeIds.delete(empId);
                }
                updateSelectAllCheckboxState();
            });

            tableBody.appendChild(tr);
        });

        renderPagination(totalPages);
        updateSelectAllCheckboxState();
    }

    // --- Pagination Controls ---
    function renderPagination(totalPages) {
        paginationControls.innerHTML = '';
        if (totalPages <= 1) return;

        const nav = document.createElement('nav');
        nav.setAttribute('aria-label', 'Staff table pagination');
        nav.className = 'pagination-nav';

        // Prev Button
        const prevBtn = document.createElement('button');
        prevBtn.type = 'button';
        prevBtn.className = 'btn-page btn-prev';
        prevBtn.innerHTML = '&larr; Prev';
        prevBtn.disabled = currentPage === 1;
        prevBtn.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                renderTable();
            }
        });
        nav.appendChild(prevBtn);

        // Numeric Page Buttons
        for (let i = 1; i <= totalPages; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.type = 'button';
            pageBtn.className = `btn-page btn-num ${i === currentPage ? 'active' : ''}`;
            pageBtn.textContent = i;
            pageBtn.addEventListener('click', () => {
                currentPage = i;
                renderTable();
            });
            nav.appendChild(pageBtn);
        }

        // Next Button
        const nextBtn = document.createElement('button');
        nextBtn.type = 'button';
        nextBtn.className = 'btn-page btn-next';
        nextBtn.innerHTML = 'Next &rarr;';
        nextBtn.disabled = currentPage === totalPages;
        nextBtn.addEventListener('click', () => {
            if (currentPage < totalPages) {
                currentPage++;
                renderTable();
            }
        });
        nav.appendChild(nextBtn);

        // Page info span
        const infoSpan = document.createElement('span');
        infoSpan.className = 'pagination-info';
        infoSpan.textContent = `Page ${currentPage} of ${totalPages} (${filteredStaff.length} employees)`;
        nav.appendChild(infoSpan);

        paginationControls.appendChild(nav);
    }

    // --- Select All Checkbox Sync ---
    function updateSelectAllCheckboxState() {
        if (!selectAllCheckbox) return;

        const startIndex = (currentPage - 1) * pageSize;
        const pageItems = filteredStaff.slice(startIndex, startIndex + pageSize);

        if (pageItems.length === 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
            return;
        }

        const selectedOnPage = pageItems.filter(item => selectedEmployeeIds.has(item.id));

        if (selectedOnPage.length === pageItems.length) {
            selectAllCheckbox.checked = true;
            selectAllCheckbox.indeterminate = false;
        } else if (selectedOnPage.length > 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = true;
        } else {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        }
    }

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', (e) => {
            const startIndex = (currentPage - 1) * pageSize;
            const pageItems = filteredStaff.slice(startIndex, startIndex + pageSize);

            if (e.target.checked) {
                pageItems.forEach(emp => selectedEmployeeIds.add(emp.id));
            } else {
                pageItems.forEach(emp => selectedEmployeeIds.delete(emp.id));
            }
            renderTable();
        });
    }

    // --- Sorting ---
    tableHeaders.forEach(th => {
        th.addEventListener('click', () => {
            const field = th.dataset.sort;
            if (!field) return;

            if (currentSort.field === field) {
                currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
            } else {
                currentSort.field = field;
                currentSort.direction = 'asc';
            }

            // Update sorting visual icons
            tableHeaders.forEach(header => {
                header.classList.remove('sort-asc', 'sort-desc');
                const icon = header.querySelector('.sort-icon');
                if (icon) icon.textContent = '';
            });

            th.classList.add(currentSort.direction === 'asc' ? 'sort-asc' : 'sort-desc');
            const icon = th.querySelector('.sort-icon');
            if (icon) {
                icon.textContent = currentSort.direction === 'asc' ? ' ▲' : ' ▼';
            }

            sortStaffData(currentSort.field, currentSort.direction);
            currentPage = 1;
            renderTable();
        });
    });

    function sortStaffData(field, direction) {
        filteredStaff.sort((a, b) => {
            let valA = (a[field] || '').toString().toLowerCase();
            let valB = (b[field] || '').toString().toLowerCase();

            let comp = 0;
            if (valA > valB) comp = 1;
            else if (valA < valB) comp = -1;

            return direction === 'asc' ? comp : -comp;
        });
    }

    // --- Filtering / Searching ---
    function applyFilter() {
        const query = (searchInput.value || '').trim().toLowerCase();
        showPreloader('Filtering staff records...');

        setTimeout(() => {
            if (!query) {
                filteredStaff = [...allStaff];
            } else {
                filteredStaff = allStaff.filter(emp => {
                    return (
                        (emp.full_name && emp.full_name.toLowerCase().includes(query)) ||
                        (emp.position && emp.position.toLowerCase().includes(query)) ||
                        (emp.phone && emp.phone.toLowerCase().includes(query)) ||
                        (emp.email && emp.email.toLowerCase().includes(query)) ||
                        (emp.url && emp.url.toLowerCase().includes(query))
                    );
                });
            }

            if (currentSort.field) {
                sortStaffData(currentSort.field, currentSort.direction);
            }

            currentPage = 1;
            renderTable();
            hidePreloader();
        }, 150); // Minor delay for smooth preloader UX
    }

    if (searchBtn) {
        searchBtn.addEventListener('click', applyFilter);
    }

    if (searchInput) {
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                applyFilter();
            }
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            searchInput.value = '';
            filteredStaff = [...allStaff];
            if (currentSort.field) {
                sortStaffData(currentSort.field, currentSort.direction);
            }
            currentPage = 1;
            renderTable();
        });
    }

    // --- Row Click Details Display ---
    function showEmployeeDetails(employee) {
        selectedEmployeeIdForDetails = employee.id;

        // Highlight active row in the table
        document.querySelectorAll('.staff-row').forEach(row => {
            row.classList.toggle('active-row', parseInt(row.dataset.id, 10) === employee.id);
        });

        const photoSrc = employee.photo_url || '/static/images/certificate_watermark.svg';

        employeeDetailsCard.innerHTML = `
            <div class="employee-details-content">
                <div class="details-photo-box">
                    <img src="${escapeHtml(photoSrc)}"
                         alt="${escapeHtml(employee.full_name)}"
                         class="details-photo-large"
                         onerror="this.src='/static/images/certificate_watermark.svg'" />
                </div>
                <div class="details-info-box">
                    <h3 class="details-name">${escapeHtml(employee.full_name)}</h3>
                    <p class="details-position"><strong>Job Title / Duties:</strong> ${escapeHtml(employee.position)}</p>
                    <p class="details-phone"><strong>Phone Number:</strong> <span class="font-mono">${escapeHtml(employee.phone)}</span></p>
                    <p class="details-email"><strong>Email Address:</strong> <a href="mailto:${escapeHtml(employee.email)}">${escapeHtml(employee.email)}</a></p>
                    <p class="details-dob"><strong>Date of Birth:</strong> ${escapeHtml(employee.date_of_birth || 'Not specified')}</p>
                    <p class="details-url">
                        <strong>Personal / Portfolio Link:</strong>
                        ${employee.url
                            ? `<a href="${escapeHtml(employee.url)}" target="_blank" rel="noopener noreferrer" class="emp-web-link">View Profile &rarr;</a>`
                            : '<span class="text-muted">None provided</span>'}
                    </p>
                </div>
            </div>
        `;
        employeeDetailsCard.style.display = 'block';
        employeeDetailsCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // --- Form Toggle ---
    if (toggleAddFormBtn && addFormPanel) {
        toggleAddFormBtn.addEventListener('click', () => {
            const isHidden = addFormPanel.style.display === 'none' || addFormPanel.style.display === '';
            addFormPanel.style.display = isHidden ? 'block' : 'none';
            toggleAddFormBtn.textContent = isHidden ? '✕ Close Add Form' : '+ Add Employee';
            if (isHidden) {
                inputFirstName.focus();
            }
        });
    }

    // --- Real-time Input Validation ---
    function checkFormValidity() {
        const fName = inputFirstName.value.trim();
        const lName = inputLastName.value.trim();
        const pos = inputPosition.value.trim();
        const email = inputEmail.value.trim();
        const dob = inputDob.value.trim();
        const phone = inputPhone.value.trim();
        const url = inputUrl.value.trim();

        const phoneRes = validatePhone(phone);
        const urlRes = validateUrl(url);

        // Highlight URL field
        if (url) {
            if (urlRes.isValid) {
                inputUrl.classList.remove('input-invalid');
                inputUrl.classList.add('input-valid');
            } else {
                inputUrl.classList.remove('input-valid');
                inputUrl.classList.add('input-invalid');
            }
        } else {
            inputUrl.classList.remove('input-valid', 'input-invalid');
        }

        // Highlight Phone field
        if (phone) {
            if (phoneRes.isValid) {
                inputPhone.classList.remove('input-invalid');
                inputPhone.classList.add('input-valid');
            } else {
                inputPhone.classList.remove('input-valid');
                inputPhone.classList.add('input-invalid');
            }
        } else {
            inputPhone.classList.remove('input-valid', 'input-invalid');
        }

        // Display validation feedback messages below form
        const feedbackMessages = [];
        if (url && !urlRes.isValid) {
            feedbackMessages.push(`⚠️ ${urlRes.message}`);
        }
        if (phone && !phoneRes.isValid) {
            feedbackMessages.push(`⚠️ ${phoneRes.message}`);
        }

        if (feedbackMessages.length > 0) {
            validationFeedback.innerHTML = feedbackMessages.map(msg => `<p class="error-msg">${escapeHtml(msg)}</p>`).join('');
            validationFeedback.style.display = 'block';
        } else if (url && phone && urlRes.isValid && phoneRes.isValid) {
            validationFeedback.innerHTML = `<p class="success-msg">✓ URL and phone formats are valid.</p>`;
            validationFeedback.style.display = 'block';
        } else {
            validationFeedback.innerHTML = '';
            validationFeedback.style.display = 'none';
        }

        // Check if all fields are valid
        const allFilled = Boolean(fName && lName && pos && email && dob && phone && url);
        const allValid = allFilled && phoneRes.isValid && urlRes.isValid;

        submitAddBtn.disabled = !allValid;
        return allValid;
    }

    // Attach real-time validation listeners
    [inputFirstName, inputLastName, inputPosition, inputEmail, inputDob, inputPhone, inputUrl].forEach(input => {
        if (input) {
            input.addEventListener('input', checkFormValidity);
            input.addEventListener('blur', checkFormValidity);
        }
    });

    // --- Submitting New Employee (Save to DB) ---
    if (addEmployeeForm) {
        addEmployeeForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!checkFormValidity()) return;

            showPreloader('Saving new employee to database...');
            submitAddBtn.disabled = true;

            const formData = new FormData(addEmployeeForm);

            try {
                const response = await fetch('/contacts/api/add/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                });

                const data = await response.json();

                if (response.ok && data.status === 'ok') {
                    showNotification(`Employee ${data.employee.full_name} successfully added!`, 'success');
                    allStaff.unshift(data.employee); // Add to beginning of list
                    filteredStaff = [...allStaff];

                    // Reset form
                    addEmployeeForm.reset();
                    [inputPhone, inputUrl].forEach(inp => inp.classList.remove('input-valid', 'input-invalid'));
                    validationFeedback.style.display = 'none';
                    addFormPanel.style.display = 'none';
                    if (toggleAddFormBtn) toggleAddFormBtn.textContent = '+ Add Employee';

                    currentPage = 1;
                    renderTable();
                    showEmployeeDetails(data.employee);
                } else {
                    showNotification(data.message || 'Error saving employee.', 'error');
                }
            } catch (err) {
                console.error('Error submitting staff member:', err);
                showNotification('Network error occurred while saving employee.', 'error');
            } finally {
                hidePreloader();
                submitAddBtn.disabled = false;
            }
        });
    }

    // --- Award Bonus Decree Generation ---
    if (awardBonusBtn) {
        awardBonusBtn.addEventListener('click', () => {
            if (selectedEmployeeIds.size === 0) {
                alert('Please select at least one employee using the checkboxes to award a bonus.');
                return;
            }

            // Extract last names (surnames) of selected employees
            const selectedStaff = allStaff.filter(emp => selectedEmployeeIds.has(emp.id));
            const surnames = selectedStaff.map(emp => {
                if (emp.last_name) return emp.last_name;
                const parts = (emp.full_name || '').split(' ');
                return parts[parts.length - 1] || emp.full_name;
            });

            const uniqueSurnames = [...new Set(surnames)].join(', ');
            const today = new Date().toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });

            bonusAnnouncementCard.innerHTML = `
                <div class="bonus-card-inner">
                    <div class="bonus-icon" aria-hidden="true">🏆</div>
                    <div class="bonus-text-content">
                        <h4>Executive Order: Annual Performance Bonus Award</h4>
                        <p class="bonus-date">Date of Decree: <em>${today}</em></p>
                        <p class="bonus-body">
                            In appreciation of outstanding confectionery excellence, exceptional work ethic,
                            and continuous dedication to artisanal standards, a celebratory quarterly bonus
                            is hereby officially awarded to the following honored staff members:
                        </p>
                        <p class="bonus-recipients"><strong>${escapeHtml(uniqueSurnames)}</strong></p>
                        <p class="bonus-signature">— Certified by Pastry Shop Management &amp; Master Bakers Guild</p>
                    </div>
                </div>
            `;
            bonusAnnouncementCard.style.display = 'block';
            bonusAnnouncementCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        });
    }

    // --- Helper Notifications ---
    function showNotification(msg, type = 'info') {
        const notif = document.createElement('div');
        notif.className = `floating-notification notif-${type}`;
        notif.textContent = msg;
        document.body.appendChild(notif);

        setTimeout(() => {
            notif.classList.add('visible');
        }, 10);

        setTimeout(() => {
            notif.classList.remove('visible');
            setTimeout(() => notif.remove(), 400);
        }, 4000);
    }

    // --- Escape HTML Helper ---
    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // --- Initial Load ---
    fetchStaffData();
});
