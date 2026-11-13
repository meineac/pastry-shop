/**
 * Pastry Shop — Theme Switcher (LR3 Item 2)
 *
 * Requirements satisfied:
 * - Option to choose theme (dark / light) using a toggle switch.
 * - When reloading or navigating pages, the chosen theme persists (localStorage).
 * - Warm, harmonic coffee-chocolate aesthetic matching the confectionery concept.
 */

(function () {
    const THEME_STORAGE_KEY = 'pastry_theme';

    /**
     * Apply chosen theme to document root element
     * @param {'dark'|'light'} theme
     */
    function applyTheme(theme) {
        const isDark = theme === 'dark';
        document.documentElement.setAttribute('data-theme', theme);

        const btn = document.getElementById('themeToggleBtn');
        if (btn) {
            const icon = btn.querySelector('.theme-toggle-icon');
            const text = btn.querySelector('.theme-toggle-text');

            if (icon) {
                icon.textContent = isDark ? '☀️' : '🌙';
            }
            if (text) {
                text.textContent = isDark ? 'Light Theme' : 'Dark Theme';
            }
            btn.setAttribute('aria-pressed', isDark ? 'true' : 'false');
            btn.setAttribute('title', isDark ? 'Switch to light theme' : 'Switch to dark theme');
        }
    }

    /**
     * Get the current effective theme from storage or system preference
     * @returns {'dark'|'light'}
     */
    function getStoredTheme() {
        const stored = localStorage.getItem(THEME_STORAGE_KEY);
        if (stored === 'dark' || stored === 'light') {
            return stored;
        }
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    // Apply immediately so there's no layout shift
    const initialTheme = getStoredTheme();
    applyTheme(initialTheme);

    // Initialize toggle button when DOM is ready
    document.addEventListener('DOMContentLoaded', () => {
        const currentTheme = getStoredTheme();
        applyTheme(currentTheme);

        const btn = document.getElementById('themeToggleBtn');
        if (!btn) return;

        btn.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme') || 'light';
            const nextTheme = current === 'dark' ? 'light' : 'dark';

            localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
            applyTheme(nextTheme);
        });
    });
})();
