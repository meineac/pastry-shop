/**
 * Pastry Shop — ES6 Slider Class (LR3 Item 1)
 *
 * Requirements satisfied:
 * - Built using ES6 class syntax (Slider).
 * - Next & Previous navigation buttons.
 * - Text captions for each slide.
 * - Slide counter display (e.g. 1/3, 2/3, 3/3).
 * - Clickable bullet pagination for direct navigation.
 * - Each slide links to its corresponding target URL.
 * - Configurable parameters:
 *    • loop: boolean (wrap around edges)
 *    • navs: boolean (toggle arrows)
 *    • pags: boolean (toggle bullets)
 *    • auto: boolean (auto-rotation, defaults to 5s if delay not specified)
 *    • stopMouseHover: boolean (pause on mouse hover when auto is true)
 *    • delay: number in seconds
 * - Interactive form element allowing administrator to dynamically change rotation delay and parameters.
 */
class Slider {
    /**
     * @param {string|HTMLElement} container - Selector or DOM node of the slider
     * @param {Object} [options={}] - Options object
     * @param {boolean} [options.loop=true]
     * @param {boolean} [options.navs=true]
     * @param {boolean} [options.pags=true]
     * @param {boolean} [options.auto=true]
     * @param {boolean} [options.stopMouseHover=true]
     * @param {number} [options.delay=5]
     */
    constructor(container, options = {}) {
        this.container = typeof container === 'string'
            ? document.querySelector(container)
            : container;

        if (!this.container) {
            console.warn('Slider: container element not found.');
            return;
        }

        this.slides = Array.from(this.container.querySelectorAll('.slider-slide'));
        if (this.slides.length === 0) {
            console.warn('Slider: no slides found inside container.');
            return;
        }

        // Parse initial options (fallback to data-attributes if available)
        const ds = this.container.dataset;
        this.options = {
            loop: options.loop !== undefined
                ? Boolean(options.loop)
                : (ds.loop !== undefined ? ds.loop === 'true' : true),
            navs: options.navs !== undefined
                ? Boolean(options.navs)
                : (ds.navs !== undefined ? ds.navs === 'true' : true),
            pags: options.pags !== undefined
                ? Boolean(options.pags)
                : (ds.pags !== undefined ? ds.pags === 'true' : true),
            auto: options.auto !== undefined
                ? Boolean(options.auto)
                : (ds.auto !== undefined ? ds.auto === 'true' : true),
            stopMouseHover: options.stopMouseHover !== undefined
                ? Boolean(options.stopMouseHover)
                : (ds.stopHover !== undefined ? ds.stopHover === 'true' : true),
            delay: Number(options.delay) > 0
                ? Number(options.delay)
                : (Number(ds.delay) > 0 ? Number(ds.delay) : 5),
        };

        this.currentIndex = 0;
        this.timer = null;
        this.isHovered = false;

        this.initDOMElements();
        this.bindEvents();
        this.updateView();

        if (this.options.auto) {
            this.startAuto();
        }
    }

    /**
     * Cache controls and generate pagination bullets.
     */
    initDOMElements() {
        this.counterEl = this.container.querySelector('.slider-counter');
        this.prevBtn = this.container.querySelector('.slider-prev');
        this.nextBtn = this.container.querySelector('.slider-next');
        this.paginationContainer = this.container.querySelector('.slider-pagination');

        // Nav visibility
        if (this.prevBtn) this.prevBtn.style.display = this.options.navs ? '' : 'none';
        if (this.nextBtn) this.nextBtn.style.display = this.options.navs ? '' : 'none';

        // Pagination bullets
        if (this.paginationContainer) {
            if (!this.options.pags) {
                this.paginationContainer.style.display = 'none';
            } else {
                this.paginationContainer.style.display = '';
                this.paginationContainer.innerHTML = '';
                this.bullets = this.slides.map((_, idx) => {
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = 'slider-bullet';
                    btn.setAttribute('aria-label', `Перейти к слайду ${idx + 1}`);
                    btn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        this.goTo(idx);
                        if (this.options.auto && !this.isHovered) {
                            this.resetAuto();
                        }
                    });
                    this.paginationContainer.appendChild(btn);
                    return btn;
                });
            }
        }
    }

    /**
     * Attach event listeners for arrows and hover pause.
     */
    bindEvents() {
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.prev();
                if (this.options.auto && !this.isHovered) {
                    this.resetAuto();
                }
            });
        }

        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.next();
                if (this.options.auto && !this.isHovered) {
                    this.resetAuto();
                }
            });
        }

        // Stop auto rotation on hover when stopMouseHover is enabled
        this.container.addEventListener('mouseenter', () => {
            this.isHovered = true;
            if (this.options.auto && this.options.stopMouseHover) {
                this.stopAuto();
            }
        });

        this.container.addEventListener('mouseleave', () => {
            this.isHovered = false;
            if (this.options.auto && this.options.stopMouseHover) {
                this.startAuto();
            }
        });
    }

    /**
     * Navigate to a specific slide index.
     * @param {number} index
     */
    goTo(index) {
        const total = this.slides.length;
        if (this.options.loop) {
            this.currentIndex = ((index % total) + total) % total;
        } else {
            this.currentIndex = Math.max(0, Math.min(index, total - 1));
        }
        this.updateView();
    }

    /**
     * Navigate to next slide.
     */
    next() {
        if (!this.options.loop && this.currentIndex >= this.slides.length - 1) {
            return;
        }
        this.goTo(this.currentIndex + 1);
    }

    /**
     * Navigate to previous slide.
     */
    prev() {
        if (!this.options.loop && this.currentIndex <= 0) {
            return;
        }
        this.goTo(this.currentIndex - 1);
    }

    /**
     * Update active slide, counter (e.g. 1/3), bullets, and arrow disabled states.
     */
    updateView() {
        const total = this.slides.length;

        // Active class on slides
        this.slides.forEach((slide, idx) => {
            if (idx === this.currentIndex) {
                slide.classList.add('active');
                slide.setAttribute('aria-hidden', 'false');
            } else {
                slide.classList.remove('active');
                slide.setAttribute('aria-hidden', 'true');
            }
        });

        // Counter: 1/3, 2/3, 3/3
        if (this.counterEl) {
            this.counterEl.textContent = `${this.currentIndex + 1}/${total}`;
        }

        // Bullets
        if (this.bullets && this.bullets.length) {
            this.bullets.forEach((bullet, idx) => {
                if (idx === this.currentIndex) {
                    bullet.classList.add('active');
                    bullet.setAttribute('aria-current', 'true');
                } else {
                    bullet.classList.remove('active');
                    bullet.removeAttribute('aria-current');
                }
            });
        }

        // Loop constraints on arrows
        if (!this.options.loop) {
            if (this.prevBtn) this.prevBtn.disabled = this.currentIndex === 0;
            if (this.nextBtn) this.nextBtn.disabled = this.currentIndex === total - 1;
        } else {
            if (this.prevBtn) this.prevBtn.disabled = false;
            if (this.nextBtn) this.nextBtn.disabled = false;
        }
    }

    /**
     * Start automatic rotation.
     */
    startAuto() {
        this.stopAuto();
        const delayMs = (this.options.delay || 5) * 1000;
        this.timer = setInterval(() => {
            this.next();
        }, delayMs);
    }

    /**
     * Stop automatic rotation.
     */
    stopAuto() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }

    /**
     * Reset rotation timer.
     */
    resetAuto() {
        this.stopAuto();
        if (this.options.auto) {
            this.startAuto();
        }
    }

    /**
     * Change delay in seconds dynamically (called by administrator form).
     * @param {number} seconds
     */
    setDelay(seconds) {
        const sec = Number(seconds);
        if (sec > 0) {
            this.options.delay = sec;
            if (this.options.auto && !this.isHovered) {
                this.resetAuto();
            }
        }
    }

    /**
     * Set loop behavior.
     * @param {boolean} enabled
     */
    setLoop(enabled) {
        this.options.loop = Boolean(enabled);
        this.updateView();
    }

    /**
     * Toggle navigation arrows.
     * @param {boolean} enabled
     */
    setNavs(enabled) {
        this.options.navs = Boolean(enabled);
        if (this.prevBtn) this.prevBtn.style.display = this.options.navs ? '' : 'none';
        if (this.nextBtn) this.nextBtn.style.display = this.options.navs ? '' : 'none';
    }

    /**
     * Toggle bullet pagination.
     * @param {boolean} enabled
     */
    setPags(enabled) {
        this.options.pags = Boolean(enabled);
        if (this.paginationContainer) {
            this.paginationContainer.style.display = this.options.pags ? '' : 'none';
            if (this.options.pags && (!this.bullets || !this.bullets.length)) {
                this.initDOMElements();
                this.updateView();
            }
        }
    }

    /**
     * Toggle automatic rotation.
     * @param {boolean} enabled
     */
    setAuto(enabled) {
        this.options.auto = Boolean(enabled);
        if (this.options.auto && !this.isHovered) {
            this.startAuto();
        } else {
            this.stopAuto();
        }
    }

    /**
     * Toggle pausing on mouse hover.
     * @param {boolean} enabled
     */
    setStopMouseHover(enabled) {
        this.options.stopMouseHover = Boolean(enabled);
    }
}

// Global initialization helper for page
document.addEventListener('DOMContentLoaded', () => {
    const sliderContainer = document.getElementById('promoSlider');
    if (!sliderContainer) return;

    // Instantiate Slider
    const slider = new Slider(sliderContainer, {
        loop: true,
        navs: true,
        pags: true,
        auto: true,
        stopMouseHover: true,
        delay: 5,
    });

    // Connect Administrator Form Controls
    const adminForm = document.getElementById('sliderAdminForm');
    const delayInput = document.getElementById('sliderDelayInput');
    const statusMsg = document.getElementById('sliderAdminStatus');

    const paramLoop = document.getElementById('sliderParamLoop');
    const paramNavs = document.getElementById('sliderParamNavs');
    const paramPags = document.getElementById('sliderParamPags');
    const paramAuto = document.getElementById('sliderParamAuto');
    const paramHover = document.getElementById('sliderParamHover');

    function updateStatus(text) {
        if (statusMsg) {
            statusMsg.textContent = text;
        }
    }

    if (adminForm && delayInput) {
        adminForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const newDelay = parseFloat(delayInput.value);
            if (newDelay && newDelay > 0) {
                slider.setDelay(newDelay);
                updateStatus(`Интервал ротации успешно изменен на ${newDelay} сек. Автопрокрутка перезапущена.`);
            } else {
                updateStatus('Пожалуйста, укажите положительное число секунд.');
            }
        });

        // Also update immediately on input change for responsive feel
        delayInput.addEventListener('change', () => {
            const newDelay = parseFloat(delayInput.value);
            if (newDelay && newDelay > 0) {
                slider.setDelay(newDelay);
                updateStatus(`Интервал ротации обновлен: ${newDelay} сек.`);
            }
        });
    }

    if (paramLoop) {
        paramLoop.addEventListener('change', (e) => {
            slider.setLoop(e.target.checked);
            updateStatus(`Зацикливание (loop): ${e.target.checked ? 'Включено' : 'Выключено'}.`);
        });
    }

    if (paramNavs) {
        paramNavs.addEventListener('change', (e) => {
            slider.setNavs(e.target.checked);
            updateStatus(`Стрелки (navs): ${e.target.checked ? 'Включены' : 'Выключены'}.`);
        });
    }

    if (paramPags) {
        paramPags.addEventListener('change', (e) => {
            slider.setPags(e.target.checked);
            updateStatus(`Пагинация (pags): ${e.target.checked ? 'Включена' : 'Выключена'}.`);
        });
    }

    if (paramAuto) {
        paramAuto.addEventListener('change', (e) => {
            slider.setAuto(e.target.checked);
            updateStatus(`Автопрокрутка (auto): ${e.target.checked ? 'Включена' : 'Выключена'}.`);
        });
    }

    if (paramHover) {
        paramHover.addEventListener('change', (e) => {
            slider.setStopMouseHover(e.target.checked);
            updateStatus(`Пауза при наведении (stopMouseHover): ${e.target.checked ? 'Включена' : 'Выключена'}.`);
        });
    }
});
