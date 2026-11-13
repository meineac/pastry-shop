/**
 * Pastry Shop — LR3 JS Lab: Task 10 (Variant 24)
 * Chart.js Visualization: Taylor Series Expansion of ln(1 - x) vs Math.log(1 - x)
 *
 * Requirements:
 * 1. Chart.js library integration.
 * 2. Plot two lines of different colors on a single coordinate axis:
 *    - F(x): Taylor series approximation: ln(1 - x) = - x - x^2/2 - x^3/3 - ... (|x| < 1)
 *    - Math F(x): Exact function value via Math.log(1 - x)
 * 3. Coordinate axes with labels, grid, legend, title, and annotation/tooltips.
 * 4. Results table with columns: x, n (number of terms), F(x), Math F(x), eps, error.
 * 5. Save graph to image file (PNG export).
 * 6. Smooth animated graph construction.
 *
 * Clean DOM manipulation: zero raw innerHTML strings for table population.
 */

(function() {
    'use strict';

    let chartInstance = null;

    // DOM Elements
    let canvas = null;
    let xMinInput = null;
    let xMaxInput = null;
    let stepInput = null;
    let epsSelect = null;
    let plotBtn = null;
    let exportBtn = null;
    let replayBtn = null;
    let tableBody = null;
    let countBadge = null;

    /**
     * Compute Taylor series for ln(1 - x)
     * Expansion: - \sum_{k=1}^\infty \frac{x^k}{k} = -x - x^2/2 - x^3/3 - ...
     * @param {number} x - Value of x where |x| < 1
     * @param {number} eps - Desired precision threshold
     * @param {number} maxTerms - Safeguard limit on iterations
     */
    function computeTaylorPoint(x, eps, maxTerms) {
        maxTerms = maxTerms || 500;
        let sum = 0;
        let n = 1;
        let xPower = x;
        let term = -x;

        // If x is exactly 0, ln(1 - 0) = ln(1) = 0
        if (Math.abs(x) < 0.0000001) {
            return {
                x: 0,
                n: 1,
                seriesVal: 0,
                mathVal: 0,
                eps: eps,
                diff: 0
            };
        }

        while (n <= maxTerms) {
            sum += term;
            if (Math.abs(term) < eps) {
                break;
            }
            n++;
            xPower *= x;
            term = -(xPower / n);
        }

        const mathVal = Math.log(1 - x);
        const diff = Math.abs(sum - mathVal);

        return {
            x: Number(x.toFixed(2)),
            n: n,
            seriesVal: Number(sum.toFixed(6)),
            mathVal: Number(mathVal.toFixed(6)),
            eps: eps,
            diff: diff < 0.000001 ? diff.toExponential(2) : Number(diff.toFixed(6))
        };
    }

    /**
     * Calculate all points across range [xMin, xMax] with step
     */
    function calculateDataPoints(xMin, xMax, step, eps) {
        const points = [];
        // Cap within convergence radius (-1, 1)
        const safeMin = Math.max(-0.99, xMin);
        const safeMax = Math.min(0.95, xMax);
        const safeStep = Math.max(0.01, step);

        for (let x = safeMin; x <= safeMax + 0.0001; x += safeStep) {
            points.push(computeTaylorPoint(x, eps));
        }
        return points;
    }

    /**
     * Populate the calculation table via clean DOM methods
     */
    function renderTable(points) {
        if (!tableBody) return;
        tableBody.innerHTML = '';

        points.forEach(function(pt) {
            const tr = tableBody.insertRow();

            // x
            const tdX = tr.insertCell();
            tdX.innerHTML = `<strong>${pt.x}</strong>`;

            // n (terms)
            const tdN = tr.insertCell();
            const nBadge = document.createElement('span');
            nBadge.className = 'calls-count-pill';
            nBadge.textContent = pt.n;
            tdN.appendChild(nBadge);

            // F(x) (Series)
            const tdSeries = tr.insertCell();
            tdSeries.className = 'val-series';
            tdSeries.textContent = pt.seriesVal.toFixed(6);

            // Math F(x)
            const tdMath = tr.insertCell();
            tdMath.className = 'val-math';
            tdMath.textContent = pt.mathVal.toFixed(6);

            // eps
            const tdEps = tr.insertCell();
            tdEps.textContent = pt.eps;

            // Absolute difference
            const tdDiff = tr.insertCell();
            tdDiff.textContent = pt.diff;
        });

        if (countBadge) {
            countBadge.textContent = points.length;
        }
    }

    /**
     * Build or update Chart.js instance
     */
    function renderChart(points) {
        if (!canvas || typeof Chart === 'undefined') return;

        const seriesData = points.map(function(pt) {
            return { x: pt.x, y: pt.seriesVal };
        });

        const mathData = points.map(function(pt) {
            return { x: pt.x, y: pt.mathVal };
        });

        // Detect dark mode for axes styling
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(44, 34, 30, 0.08)';
        const textColor = isDark ? '#f5ede3' : '#2c221e';

        if (chartInstance) {
            chartInstance.destroy();
        }

        const ctx = canvas.getContext('2d');
        chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [
                    {
                        label: 'F(x) — Taylor Series Expansion',
                        data: seriesData,
                        borderColor: '#8b3a2b',       // Pastry Primary (Rich Berry)
                        backgroundColor: 'rgba(139, 58, 43, 0.12)',
                        borderWidth: 3,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        pointBackgroundColor: '#8b3a2b',
                        tension: 0.25,
                        fill: false
                    },
                    {
                        label: 'Math F(x) — Math.log(1 - x)',
                        data: mathData,
                        borderColor: '#27ae60',       // Accent Emerald Green
                        backgroundColor: 'rgba(39, 174, 96, 0.1)',
                        borderWidth: 2,
                        borderDash: [6, 4],
                        pointRadius: 3,
                        pointHoverRadius: 5,
                        pointBackgroundColor: '#27ae60',
                        tension: 0.25,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 1200,
                    easing: 'easeOutQuart'
                },
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Comparison: Taylor Series Expansion of ln(1 - x) vs Exact Math.log(1 - x)',
                        color: textColor,
                        font: {
                            size: 15,
                            family: 'Playfair Display, Georgia, serif',
                            weight: '600'
                        },
                        padding: {
                            top: 10,
                            bottom: 15
                        }
                    },
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: textColor,
                            usePointStyle: true,
                            padding: 15,
                            font: {
                                size: 12,
                                family: 'Montserrat, sans-serif',
                                weight: '500'
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(44, 34, 30, 0.95)',
                        titleColor: '#ffd885',
                        bodyColor: '#ffffff',
                        padding: 10,
                        boxPadding: 4,
                        usePointStyle: true,
                        callbacks: {
                            title: function(items) {
                                if (!items || items.length === 0) return '';
                                return 'Argument x = ' + items[0].parsed.x;
                            },
                            label: function(context) {
                                const val = context.parsed.y;
                                return ' ' + context.dataset.label + ': ' + val.toFixed(6);
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        title: {
                            display: true,
                            text: 'Argument x (|x| < 1)',
                            color: textColor,
                            font: { size: 13, weight: '600', family: 'Montserrat, sans-serif' }
                        },
                        grid: {
                            color: gridColor
                        },
                        ticks: {
                            color: textColor
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Function Value y',
                            color: textColor,
                            font: { size: 13, weight: '600', family: 'Montserrat, sans-serif' }
                        },
                        grid: {
                            color: gridColor
                        },
                        ticks: {
                            color: textColor
                        }
                    }
                }
            }
        });
    }

    /**
     * Calculate and update everything (Chart + Table)
     */
    function updatePlot() {
        const xMin = parseFloat(xMinInput ? xMinInput.value : -0.9) || -0.9;
        const xMax = parseFloat(xMaxInput ? xMaxInput.value : 0.8) || 0.8;
        const step = parseFloat(stepInput ? stepInput.value : 0.1) || 0.1;
        const eps = parseFloat(epsSelect ? epsSelect.value : 0.0001) || 0.0001;

        const points = calculateDataPoints(xMin, xMax, step, eps);
        renderTable(points);
        renderChart(points);
    }

    /**
     * Save chart to PNG file
     */
    function exportChart() {
        if (!canvas) return;

        // Force a white or dark solid background for exported image so it is readable outside the browser
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = canvas.width;
        tempCanvas.height = canvas.height;
        const tempCtx = tempCanvas.getContext('2d');

        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        tempCtx.fillStyle = isDark ? '#1a1412' : '#ffffff';
        tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
        tempCtx.drawImage(canvas, 0, 0);

        const imageUri = tempCanvas.toDataURL('image/png');
        const link = document.createElement('a');
        link.download = 'taylor_series_ln_1_minus_x.png';
        link.href = imageUri;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    /**
     * Replay Chart.js animation
     */
    function replayAnimation() {
        if (chartInstance) {
            chartInstance.reset();
            chartInstance.update();
        }
    }

    /**
     * Initialize Task 10
     */
    function init() {
        canvas = document.getElementById('taylorChart');
        xMinInput = document.getElementById('chartXMinInput');
        xMaxInput = document.getElementById('chartXMaxInput');
        stepInput = document.getElementById('chartStepInput');
        epsSelect = document.getElementById('chartEpsSelect');
        plotBtn = document.getElementById('plotChartBtn');
        exportBtn = document.getElementById('exportChartBtn');
        replayBtn = document.getElementById('replayChartAnimBtn');
        tableBody = document.getElementById('seriesTableBody');
        countBadge = document.getElementById('seriesRowsCount');

        if (!canvas) return;

        // Initial plot
        updatePlot();

        if (plotBtn) plotBtn.addEventListener('click', updatePlot);
        if (exportBtn) exportBtn.addEventListener('click', exportChart);
        if (replayBtn) replayBtn.addEventListener('click', replayAnimation);

        // Update chart colors on theme switch
        const themeBtn = document.getElementById('themeToggleBtn');
        if (themeBtn) {
            themeBtn.addEventListener('click', function() {
                setTimeout(updatePlot, 50);
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
