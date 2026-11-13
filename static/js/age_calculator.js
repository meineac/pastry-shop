/**
 * Pastry Shop — LR3 JS Lab: Task 7
 * Age & Weekday Calculator with Minor Parental Permission Alert
 *
 * Requirements:
 * 1. Request user's date of birth.
 * 2. Calculate exact age in full completed years.
 * 3. Display the day of the week of the entered birth date for adults (age >= 18).
 * 4. Trigger an alert requesting parental permission if the user is a minor (age < 18).
 *
 * Implementation:
 * Clean, safe DOM manipulation using textContent and pre-structured HTML templates.
 * Zero raw HTML string injection.
 */

(function() {
    'use strict';

    const WEEKDAYS = [
        'Sunday',
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday'
    ];

    // DOM Elements
    let form = null;
    let birthDateInput = null;
    let resetBtn = null;
    let presetButtons = null;

    // Results container and cards
    let resultContainer = null;
    let adultResultCard = null;
    let minorResultCard = null;
    let errorResultCard = null;

    // Adult card fields
    let adultAgeVal = null;
    let adultDayVal = null;
    let adultDateVal = null;
    let adultMsgDay = null;
    let adultTimestamp = null;

    // Minor card fields
    let minorAgeVal = null;
    let minorDayVal = null;
    let minorDateVal = null;
    let minorTimestamp = null;

    // Error card fields
    let errorResultTitle = null;
    let errorResultMessage = null;

    /**
     * Calculate age in full completed years
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
     * Hide all result cards
     */
    function hideAllResults() {
        if (!resultContainer) return;
        resultContainer.hidden = true;
        adultResultCard.hidden = true;
        minorResultCard.hidden = true;
        errorResultCard.hidden = true;
    }

    /**
     * Show Error Card
     */
    function showError(title, message) {
        hideAllResults();
        errorResultTitle.textContent = title;
        errorResultMessage.textContent = message;
        errorResultCard.hidden = false;
        resultContainer.hidden = false;
    }

    /**
     * Process birth date calculation and update UI
     */
    function processDate(dateString) {
        if (!dateString) {
            showError('Date Required', 'Please select or enter your date of birth.');
            return;
        }

        const parts = dateString.split('-');
        if (parts.length !== 3) {
            showError('Invalid Format', 'Please enter a valid date in YYYY-MM-DD format.');
            return;
        }

        const year = parseInt(parts[0], 10);
        const month = parseInt(parts[1], 10) - 1;
        const day = parseInt(parts[2], 10);

        const birthDate = new Date(year, month, day);
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

        if (isNaN(birthDate.getTime())) {
            showError('Invalid Date', 'Could not parse the selected date.');
            return;
        }

        if (birthDate > today) {
            showError('Future Date Detected', 'Birth date cannot be in the future. Please select a valid past date.');
            return;
        }

        const age = calculateAge(birthDate, today);
        const dayOfWeek = WEEKDAYS[birthDate.getDay()];
        const formattedBirthDate = formatDate(birthDate);
        const isAdult = age >= 18;

        hideAllResults();

        if (isAdult) {
            // Populate adult card fields
            adultAgeVal.textContent = age;
            adultDayVal.textContent = dayOfWeek;
            adultDateVal.textContent = formattedBirthDate;
            adultMsgDay.textContent = dayOfWeek;
            adultTimestamp.textContent = 'Verified on ' + formatDate(now);

            adultResultCard.hidden = false;
            resultContainer.hidden = false;
        } else {
            // Populate minor card fields
            minorAgeVal.textContent = age;
            minorDayVal.textContent = dayOfWeek;
            minorDateVal.textContent = formattedBirthDate;
            minorTimestamp.textContent = 'Checked on ' + formatDate(now);

            minorResultCard.hidden = false;
            resultContainer.hidden = false;

            // Trigger browser alert as required by specification
            setTimeout(function() {
                alert(
                    'Parental Permission Required!\n\n' +
                    'You are ' + age + ' years old (minor).\n' +
                    'You need permission from your parents or legal guardians to use this website.'
                );
            }, 50);
        }

        resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Initialize DOM references and event listeners
     */
    function init() {
        form = document.getElementById('ageCalculatorForm');
        birthDateInput = document.getElementById('birthDateInput');
        resetBtn = document.getElementById('resetAgeBtn');
        presetButtons = document.querySelectorAll('.age-preset-btn');

        resultContainer = document.getElementById('ageResultContainer');
        adultResultCard = document.getElementById('adultResultCard');
        minorResultCard = document.getElementById('minorResultCard');
        errorResultCard = document.getElementById('errorResultCard');

        adultAgeVal = document.getElementById('adultAgeVal');
        adultDayVal = document.getElementById('adultDayVal');
        adultDateVal = document.getElementById('adultDateVal');
        adultMsgDay = document.getElementById('adultMsgDay');
        adultTimestamp = document.getElementById('adultTimestamp');

        minorAgeVal = document.getElementById('minorAgeVal');
        minorDayVal = document.getElementById('minorDayVal');
        minorDateVal = document.getElementById('minorDateVal');
        minorTimestamp = document.getElementById('minorTimestamp');

        errorResultTitle = document.getElementById('errorResultTitle');
        errorResultMessage = document.getElementById('errorResultMessage');

        if (!form || !birthDateInput) return;

        // Restrict input max to today
        const now = new Date();
        const yyyy = now.getFullYear();
        const mm = String(now.getMonth() + 1).padStart(2, '0');
        const dd = String(now.getDate()).padStart(2, '0');
        birthDateInput.max = `${yyyy}-${mm}-${dd}`;

        // Form submission
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            processDate(birthDateInput.value);
        });

        // Form reset
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                birthDateInput.value = '';
                hideAllResults();
                birthDateInput.focus();
            });
        }

        // Test presets
        if (presetButtons) {
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

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
