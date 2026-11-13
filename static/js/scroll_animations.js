/**
 * Pastry Shop — LR3: Task 11 (Variant 24)
 * Full-Page Scroll-Driven Pastry Animation
 *
 * Requirements:
 * - Confectionery theme: Flying pastries/cookies that continuously rotate and change size (scale).
 * - Animation spans across the full page (not boxed in a container).
 * - Synchronized with scroll: moves forward when scrolling down, and reverses when scrolling back up.
 * - Optimized with window.requestAnimationFrame for fluid 60 FPS performance.
 */

(function() {
    'use strict';

    let container = null;
    let pastries = [];
    let scrollPosDisplay = null;
    let scrollDirDisplay = null;

    let lastScrollY = window.scrollY;
    let isTicking = false;

    /**
     * Recalculates coordinates, continuous rotation, and scaling factor for all pastries
     */
    function updatePastries() {
        if (!pastries.length) return;

        const currentScrollY = window.scrollY;
        const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
        // Normalized scroll progress across the entire document [0.0 to 1.0]
        const progress = maxScroll > 0 ? Math.min(1, Math.max(0, currentScrollY / maxScroll)) : 0;

        // Detect direction for telemetry display
        let direction = 'Static';
        if (currentScrollY > lastScrollY) {
            direction = 'Scrolling Down ↓';
        } else if (currentScrollY < lastScrollY) {
            direction = 'Scrolling Up ↑';
        }
        lastScrollY = currentScrollY;

        if (scrollPosDisplay) {
            scrollPosDisplay.textContent = Math.round(currentScrollY) + 'px';
        }
        if (scrollDirDisplay) {
            scrollDirDisplay.textContent = direction;
        }

        const vpWidth = window.innerWidth;
        const vpHeight = window.innerHeight;

        // Animate each pastry across the full viewport
        pastries.forEach(function(item) {
            const startX = parseFloat(item.getAttribute('data-start-x')) || 10;
            const startY = parseFloat(item.getAttribute('data-start-y')) || 10;
            const deltaX = parseFloat(item.getAttribute('data-delta-x')) || 50;
            const deltaY = parseFloat(item.getAttribute('data-delta-y')) || 50;
            const rotFactor = parseFloat(item.getAttribute('data-rot')) || 1.0;
            const scaleAmp = parseFloat(item.getAttribute('data-scale-amp')) || 0.4;
            const baseScale = parseFloat(item.getAttribute('data-base-scale')) || 1.0;

            // Coordinate interpolation across full screen width and height
            const posX = (startX / 100) * vpWidth + (deltaX / 100) * vpWidth * progress;
            const posY = (startY / 100) * vpHeight + (deltaY / 100) * vpHeight * progress;

            // Continuous rotation directly proportional to scroll offset (spins forward and backward)
            const rotation = currentScrollY * rotFactor;

            // Dynamic sinusoidal scaling based on document progress
            const scale = Math.max(0.5, baseScale + Math.sin(progress * Math.PI * 4) * scaleAmp);

            // Apply 3D transform for GPU acceleration and smooth 60 FPS motion
            item.style.transform = `translate3d(${posX.toFixed(1)}px, ${posY.toFixed(1)}px, 0) rotate(${rotation.toFixed(1)}deg) scale(${scale.toFixed(2)})`;
        });

        isTicking = false;
    }

    /**
     * Scroll event handler throttled with requestAnimationFrame
     */
    function onScroll() {
        if (!isTicking) {
            window.requestAnimationFrame(updatePastries);
            isTicking = true;
        }
    }

    /**
     * Initializes the full-page animation
     */
    function init() {
        container = document.getElementById('fullpagePastryContainer');
        if (!container) return;

        pastries = Array.from(container.querySelectorAll('.flying-pastry'));
        scrollPosDisplay = document.getElementById('scrollPosDisplay');
        scrollDirDisplay = document.getElementById('scrollDirDisplay');

        // Event listeners with passive flag for smooth browser scrolling
        window.addEventListener('scroll', onScroll, { passive: true });
        window.addEventListener('resize', onScroll, { passive: true });

        // Initial render on page load
        updatePastries();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
