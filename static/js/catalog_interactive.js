/**
 * Pastry Shop — Catalog Interactivity (LR3 Items 5 & 6)
 * 
 * Item 5: Client-side pagination (default 3 items per page, selectable page size,
 *         numeric user navigation, responsive controls).
 * Item 6: 3D volume / tilt / parallax hover effect on product cards
 *         following the CodePen example (https://codepen.io/ghaste/pen/zYJqxax).
 */

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', initCatalogInteractivity);

    function initCatalogInteractivity() {
        const productGrid = document.querySelector('.catalog-page .product-grid');
        const cardWrappers = Array.from(document.querySelectorAll('.catalog-page .product-grid > .card-wrapper'));

        // Fallback: if cards aren't wrapped in .card-wrapper yet, query .product-card
        const items = cardWrappers.length > 0
            ? cardWrappers
            : Array.from(document.querySelectorAll('.catalog-page .product-grid > .product-card'));

        // Initialize 3D card tilt for all product cards (Item 6)
        initCard3DTilt(items);

        // Initialize client-side pagination if items exist (Item 5)
        if (productGrid && items.length > 0) {
            initCatalogPagination(productGrid, items);
        }
    }

    /* ==========================================================================
       ITEM 5: CLIENT-SIDE PAGINATION WITH SELECTABLE PAGE SIZE
       ========================================================================== */
    function initCatalogPagination(productGrid, items) {
        const totalItems = items.length;

        // Default page size: 3 items (as required by LR3)
        let pageSize = 3;
        let currentPage = 1;

        const pageSizeSelect = document.getElementById('catalog-page-size');
        const summaryElement = document.getElementById('catalog-summary');
        const paginationContainer = document.getElementById('catalog-pagination');

        if (!paginationContainer) {
            return;
        }

        // Listen for page size changes
        if (pageSizeSelect) {
            pageSizeSelect.addEventListener('change', (e) => {
                const selectedVal = e.target.value;
                if (selectedVal === 'all') {
                    pageSize = totalItems;
                } else {
                    pageSize = parseInt(selectedVal, 10) || 3;
                }
                currentPage = 1;
                render();
            });
        }

        function calculateTotalPages() {
            return Math.ceil(totalItems / pageSize) || 1;
        }

        function render() {
            const totalPages = calculateTotalPages();
            if (currentPage > totalPages) currentPage = totalPages;
            if (currentPage < 1) currentPage = 1;

            const startIndex = (currentPage - 1) * pageSize;
            const endIndex = startIndex + pageSize;

            // Toggle visibility of each item
            items.forEach((item, index) => {
                if (index >= startIndex && index < endIndex) {
                    item.style.display = '';
                    item.removeAttribute('aria-hidden');
                } else {
                    item.style.display = 'none';
                    item.setAttribute('aria-hidden', 'true');
                }
            });

            // Update summary text
            if (summaryElement) {
                const currentShowingEnd = Math.min(endIndex, totalItems);
                if (totalItems === 0) {
                    summaryElement.textContent = 'No products available.';
                } else if (pageSize >= totalItems) {
                    summaryElement.textContent = `Showing all ${totalItems} products`;
                } else {
                    summaryElement.textContent = `Showing ${startIndex + 1}–${currentShowingEnd} of ${totalItems} products (Page ${currentPage} of ${totalPages})`;
                }
            }

            // Render navigation buttons
            renderPaginationNav(totalPages);
        }

        function renderPaginationNav(totalPages) {
            paginationContainer.innerHTML = '';

            if (totalPages <= 1) {
                return;
            }

            const nav = document.createElement('nav');
            nav.className = 'pagination-nav';
            nav.setAttribute('aria-label', 'Catalog page navigation');

            // First Page Button (<<)
            const firstBtn = document.createElement('button');
            firstBtn.type = 'button';
            firstBtn.className = 'btn-page btn-first';
            firstBtn.innerHTML = '&laquo; First';
            firstBtn.title = 'Go to first page';
            firstBtn.disabled = currentPage === 1;
            firstBtn.addEventListener('click', () => {
                if (currentPage !== 1) goToPage(1);
            });
            nav.appendChild(firstBtn);

            // Previous Button (<)
            const prevBtn = document.createElement('button');
            prevBtn.type = 'button';
            prevBtn.className = 'btn-page btn-prev';
            prevBtn.innerHTML = '&larr; Prev';
            prevBtn.title = 'Go to previous page';
            prevBtn.disabled = currentPage === 1;
            prevBtn.addEventListener('click', () => {
                if (currentPage > 1) goToPage(currentPage - 1);
            });
            nav.appendChild(prevBtn);

            // Numeric Page Buttons with Sliding Window
            const pageNumbers = getPageNumbersWindow(currentPage, totalPages);
            pageNumbers.forEach(item => {
                if (item === '...') {
                    const ellipsisSpan = document.createElement('span');
                    ellipsisSpan.className = 'pagination-ellipsis';
                    ellipsisSpan.textContent = '…';
                    ellipsisSpan.setAttribute('aria-hidden', 'true');
                    nav.appendChild(ellipsisSpan);
                } else {
                    const pageNum = item;
                    const pageBtn = document.createElement('button');
                    pageBtn.type = 'button';
                    pageBtn.className = `btn-page${pageNum === currentPage ? ' active' : ''}`;
                    pageBtn.textContent = pageNum;
                    pageBtn.title = `Page ${pageNum}`;
                    if (pageNum === currentPage) {
                        pageBtn.setAttribute('aria-current', 'page');
                    }
                    pageBtn.addEventListener('click', () => {
                        if (currentPage !== pageNum) goToPage(pageNum);
                    });
                    nav.appendChild(pageBtn);
                }
            });

            // Next Button (>)
            const nextBtn = document.createElement('button');
            nextBtn.type = 'button';
            nextBtn.className = 'btn-page btn-next';
            nextBtn.innerHTML = 'Next &rarr;';
            nextBtn.title = 'Go to next page';
            nextBtn.disabled = currentPage === totalPages;
            nextBtn.addEventListener('click', () => {
                if (currentPage < totalPages) goToPage(currentPage + 1);
            });
            nav.appendChild(nextBtn);

            // Last Page Button (>>)
            const lastBtn = document.createElement('button');
            lastBtn.type = 'button';
            lastBtn.className = 'btn-page btn-last';
            lastBtn.innerHTML = 'Last &raquo;';
            lastBtn.title = 'Go to last page';
            lastBtn.disabled = currentPage === totalPages;
            lastBtn.addEventListener('click', () => {
                if (currentPage !== totalPages) goToPage(totalPages);
            });
            nav.appendChild(lastBtn);

            paginationContainer.appendChild(nav);
        }

        function goToPage(page) {
            currentPage = page;
            render();

            const toolbar = document.getElementById('catalog-toolbar') || productGrid;
            if (toolbar) {
                const rect = toolbar.getBoundingClientRect();
                if (rect.top < 0) {
                    window.scrollTo({
                        top: window.scrollY + rect.top - 20,
                        behavior: 'smooth'
                    });
                }
            }
        }

        function getPageNumbersWindow(current, total) {
            if (total <= 7) {
                const pages = [];
                for (let i = 1; i <= total; i++) pages.push(i);
                return pages;
            }

            const pages = [];
            pages.push(1);

            let left = current - 1;
            let right = current + 1;

            if (current <= 3) {
                left = 2;
                right = 4;
            } else if (current >= total - 2) {
                left = total - 3;
                right = total - 1;
            }

            if (left > 2) pages.push('...');
            for (let i = left; i <= right; i++) {
                if (i > 1 && i < total) pages.push(i);
            }
            if (right < total - 1) pages.push('...');

            pages.push(total);
            return pages;
        }

        // Initial render
        render();
    }


    /* ==========================================================================
       ITEM 6: 3D VOLUME / TILT HOVER EFFECT (CodePen Reference Implementation)
       ========================================================================== */
    function initCard3DTilt(cardWrappers) {
        cardWrappers.forEach(card_w => {
            const card = card_w.querySelector('.card') || card_w;
            if (!card) return;

            card_w.addEventListener('mouseenter', () => {
                card.style.animation = 'unset';
            });

            card_w.addEventListener('mousemove', event => {
                const rect = card_w.getBoundingClientRect();
                const x = event.clientX - rect.left;
                const y = event.clientY - rect.top;
                const width = rect.width;
                const height = rect.height;

                if (!width || !height) return;

                const middleX = width / 2;
                const middleY = height / 2;
                const offsetX = ((x - middleX) / middleX) * 25;
                const offsetY = ((y - middleY) / middleY) * 25;
                const offX = 50 + ((x - middleX) / middleX) * 25;
                const offY = 50 - ((y - middleY) / middleY) * 20;

                card.style.setProperty('--rotateX', (1 * offsetX) + 'deg');
                card.style.setProperty('--rotateY', (-1 * offsetY) + 'deg');
                card.style.setProperty('--posx', offX + '%');
                card.style.setProperty('--posy', offY + '%');
            });

            card_w.addEventListener('mouseleave', () => {
                card.style.animation = 'reset-card 1s ease';
                card.addEventListener('animationend', () => {
                    card.style.animation = 'unset';
                    card.style.setProperty('--rotateX', '0deg');
                    card.style.setProperty('--rotateY', '0deg');
                    card.style.setProperty('--posx', '50%');
                    card.style.setProperty('--posy', '50%');
                }, { once: true });
            });
        });
    }

})();
