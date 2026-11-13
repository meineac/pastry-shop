/**
 * Pastry Shop — LR3 JS Lab: Task 7
 * Age & Weekday Calculator with Minor Parental Permission Alert
 *
 * Requirements:
 * 1. Request user's date of birth.
 * 2. Calculate the exact age in full completed years.
 * 3. Display the day of the week of the entered birth date for adults (age >= 18).
 * 4. Trigger a browser alert requesting parental permission to use the website if the user is a minor (age < 18).
 * 5. Everything in English, simple, clean, and robust.
 */

(function() {
    'use strict';

    // DOM Elements
    let form = null;
    let birthDateInput = null;
    let resultContainer = null;
    let resetBtn = null;
    let presetButtons = null;

    const WEEKDAYS = [
        'Sunday',
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday'
    ];

    /**
     * Calculate age in full completed years
     * @param {Date} birthDate
     * @param {Date} currentDate
     * @returns {number}
     */
    function calculateAge(birthDate, currentDate) {
        let age = currentDate.getFullYear() - birthDate.getFullYear();
        const monthDiff = currentDate.getMonth() - birthDate.getMonth();
        if (monthDiff < 0 || (monthDiff === 0 && currentDate.getDate() < birthDate.getDate())) {
            age--;
        }
        return age;
    }

    /**
     * Format Date to English readable string (e.g. October 15, 2000)
     */
    function formatDate(date) {
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    /**
     * Escape special HTML characters
     */
    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    /**
     * Process birth date calculation and display results
     */
    function processDate(dateString) {
        if (!dateString) {
            renderMessage('error', 'Date Required', 'Please select or enter your date of birth.');
            return;
        }

        // Parse date values explicitly to avoid timezone off-by-one errors
        const parts = dateString.split('-');
        if (parts.length !== 3) {
            renderMessage('error', 'Invalid Format', 'Please enter a valid date in YYYY-MM-DD format.');
            return;
        }

        const year = parseInt(parts[0], 10);
        const month = parseInt(parts[1], 10) - 1; // 0-indexed month
        const day = parseInt(parts[2], 10);

        const birthDate = new Date(year, month, day);
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

        // Validate date
        if (isNaN(birthDate.getTime())) {
            renderMessage('error', 'Invalid Date', 'Could not parse the selected date.');
            return;
        }

        if (birthDate > today) {
            renderMessage('error', 'Future Date Detected', 'Birth date cannot be in the future. Please select a valid past date.');
            return;
        }

        const age = calculateAge(birthDate, today);
        const dayOfWeek = WEEKDAYS[birthDate.getDay()];
        const formattedBirthDate = formatDate(birthDate);
        const isAdult = age >= 18;

        if (isAdult) {
            // Requirement: "сообщение о дне недели введенной даты для совершеннолетних"
            renderAdultResult(age, dayOfWeek, formattedBirthDate);
        } else {
            // Requirement: "алерт о необходимости разрешения родителей на использование сайта, если несовершеннолетний"
            renderMinorResult(age, dayOfWeek, formattedBirthDate);

            // Trigger the browser alert required by the assignment
            setTimeout(function() {
                alert(
                    'Parental Permission Required!\n\n' +
                    'You are ' + age + ' years old (minor).\n' +
                    'You need permission from your parents or legal guardians to use this website and browse confectionery products.'
                );
            }, 50);
        }
    }

    /**
     * Render result card for Adult (age >= 18)
     */
    function renderAdultResult(age, dayOfWeek, formattedDate) {
        if (!resultContainer) return;

        resultContainer.style.display = 'block';
        resultContainer.innerHTML = `
            <div class="age-result-card result-adult" role="region" aria-label="Adult verification result">
                <div class="result-header">
                    <span class="result-badge badge-adult">Adult (&ge; 18)</span>
                    <span class="result-timestamp">Verified on ${formatDate(new Date())}</span>
                </div>
                <div class="result-body">
                    <h3 class="result-title">Welcome to Pastry Shop!</h3>
                    <div class="result-stat-grid">
                        <div class="stat-item">
                            <span class="stat-label">Calculated Age</span>
                            <span class="stat-value"><strong>${age}</strong> full years</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Day of the Week</span>
                            <span class="stat-value highlight-day"><strong>${escapeHtml(dayOfWeek)}</strong></span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Birth Date</span>
                            <span class="stat-value">${escapeHtml(formattedDate)}</span>
                        </div>
                    </div>
                    <div class="result-notice notice-success">
                        <p>
                            🎉 <strong>Day of Week Message:</strong> You were born on a <strong>${escapeHtml(dayOfWeek)}</strong>!
                            As a verified adult (18+), you have full access to our online bakery catalog, ordering, and customer features.
                        </p>
                    </div>
                </div>
            </div>
        `;

        resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Render result card for Minor (age < 18)
     */
    function renderMinorResult(age, dayOfWeek, formattedDate) {
        if (!resultContainer) return;

        resultContainer.style.display = 'block';
        resultContainer.innerHTML = `
            <div class="age-result-card result-minor" role="region" aria-label="Minor verification result">
                <div class="result-header">
                    <span class="result-badge badge-minor">Minor (&lt; 18)</span>
                    <span class="result-timestamp">Checked on ${formatDate(new Date())}</span>
                </div>
                <div class="result-body">
                    <h3 class="result-title text-danger">Parental Permission Required</h3>
                    <div class="result-stat-grid">
                        <div class="stat-item">
                            <span class="stat-label">Calculated Age</span>
                            <span class="stat-value"><strong>${age}</strong> years old</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Day of Birth</span>
                            <span class="stat-value"><strong>${escapeHtml(dayOfWeek)}</strong></span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Birth Date</span>
                            <span class="stat-value">${escapeHtml(formattedDate)}</span>
                        </div>
                    </div>
                    <div class="result-notice notice-danger">
                        <p>
                            ⚠️ <strong>Attention:</strong> Because you are under 18 years of age, you are required to have
                            explicit permission from a parent or legal guardian to use this website.
                            A browser alert has also been displayed.
                        </p>
                    </div>
                </div>
            </div>
        `;

        resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Render general validation/error message
     */
    function renderMessage(type, title, text) {
        if (!resultContainer) return;

        resultContainer.style.display = 'block';
        resultContainer.innerHTML = `
            <div class="age-result-card result-${type}">
                <h4 style="margin: 0 0 0.35rem 0; color: var(--color-primary);">${escapeHtml(title)}</h4>
                <p style="margin: 0; color: var(--color-text);">${escapeHtml(text)}</p>
            </div>
        `;
    }

    /**
     * Initialize the component
     */
    function init() {
        form = document.getElementById('ageCalculatorForm');
        birthDateInput = document.getElementById('birthDateInput');
        resultContainer = document.getElementById('ageResultContainer');
        resetBtn = document.getElementById('resetAgeBtn');
        presetButtons = document.querySelectorAll('.age-preset-btn');

        if (!form || !birthDateInput) {
            return;
        }

        // Restrict input max to today
        const now = new Date();
        const yyyy = now.getFullYear();
        const mm = String(now.getMonth() + 1).padStart(2, '0');
        const dd = String(now.getDate()).padStart(2, '0');
        birthDateInput.max = `${yyyy}-${mm}-${dd}`;

        // Handle form submission
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            processDate(birthDateInput.value);
        });

        // Handle Reset
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                birthDateInput.value = '';
                if (resultContainer) {
                    resultContainer.style.display = 'none';
                    resultContainer.innerHTML = '';
                }
                birthDateInput.focus();
            });
        }

        // Handle quick test preset buttons
        if (presetButtons && presetButtons.length > 0) {
            presetButtons.forEach(function(btn) {
                btn.addEventListener('click', function() {
                    const yearsAgo = parseInt(this.getAttribute('data-years-ago'), 10);
                    if (!isNaN(yearsAgo)) {
                        const target = new Date();
                        target.setFullYear(target.getFullYear() - yearsAgo);
                        const y = target.getFullYear();
                        const m = String(target.getMonth() + 1).padStart(2, '0');
                        const d = String(target.getDate()).padStart(2, '0');
                        const dateStr = `${y}-${m}-${d}`;
                        birthDateInput.value = dateStr;
                        processDate(dateStr);
                    }
                });
            });
        }
    }

    // Attach to DOMContentLoaded or run immediately if ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
