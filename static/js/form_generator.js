/**
 * Pastry Shop — LR3 JS Lab: Task 4 (Variant 24)
 * Dynamic Form Element Generator (<textarea>)
 *
 * Requirements:
 * 1. Checkbox triggers dynamic generation of the form element (<textarea>).
 * 2. Interactive setup of attributes (generated simultaneously with the element):
 *    - name, rows, cols, placeholder, maxlength, wrap, readonly.
 * 3. Reactive binding: changes in attribute fields immediately apply to the <textarea>.
 * 4. Multiple elements can be added.
 * 5. Deletion of individual elements.
 * 6. Persistent state in localStorage across page reloads.
 */

(function() {
    'use strict';

    const STORAGE_KEY = 'pastry_generated_textareas';

    // State array holding all active textarea items
    let items = [];

    // DOM References
    let triggerCheckbox = null;
    let actionsBar = null;
    let addMoreBtn = null;
    let clearAllBtn = null;
    let emptyState = null;
    let container = null;
    let countBadge = null;

    /**
     * Escape special HTML characters for safe markup generation
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
     * Load state from localStorage
     */
    function loadState() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (raw) {
                const parsed = JSON.parse(raw);
                if (Array.isArray(parsed)) {
                    items = parsed;
                }
            }
        } catch (e) {
            console.error('Failed to load textareas from localStorage:', e);
            items = [];
        }
    }

    /**
     * Save state to localStorage
     */
    function saveState() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
        } catch (e) {
            console.error('Failed to save textareas to localStorage:', e);
        }
    }

    /**
     * Generate HTML snippet representation for display
     */
    function buildHtmlSnippet(item) {
        const parts = ['<textarea'];
        if (item.name) parts.push(`name="${escapeHtml(item.name)}"`);
        if (item.rows) parts.push(`rows="${item.rows}"`);
        if (item.cols) parts.push(`cols="${item.cols}"`);
        if (item.placeholder) parts.push(`placeholder="${escapeHtml(item.placeholder)}"`);
        if (item.maxlength !== null && item.maxlength !== undefined && item.maxlength !== '') {
            parts.push(`maxlength="${item.maxlength}"`);
        }
        if (item.wrap) parts.push(`wrap="${escapeHtml(item.wrap)}"`);
        if (item.readonly) parts.push('readonly');
        parts.push(`>${escapeHtml(item.value || '')}</textarea>`);
        return parts.join(' ');
    }

    /**
     * Create default data for a new textarea element
     */
    function createNewItemData() {
        const index = items.length + 1;
        const id = 'ta_' + Date.now() + '_' + Math.floor(Math.random() * 1000);
        return {
            id: id,
            name: `pastry_feedback_${index}`,
            rows: 4,
            cols: 40,
            placeholder: 'Enter your special pastry request or custom feedback here...',
            maxlength: 250,
            wrap: 'soft',
            readonly: false,
            value: ''
        };
    }

    /**
     * Create DOM card for a single textarea item
     */
    function renderCard(item, index) {
        const card = document.createElement('article');
        card.className = 'textarea-item-card card-box';
        card.id = `card-${item.id}`;
        card.setAttribute('data-id', item.id);

        card.innerHTML = `
            <header class="card-item-header">
                <div class="card-item-title-group">
                    <span class="card-item-counter">#${index + 1}</span>
                    <h3 class="card-item-title">&lt;textarea&gt; Form Element</h3>
                    <code class="badge-tag">&lt;textarea name="${escapeHtml(item.name)}"&gt;</code>
                </div>
                <div class="card-item-actions">
                    <button type="button" class="btn btn-sm btn-delete-item" data-action="delete" title="Delete this element from the page">
                        <span aria-hidden="true">🗑️</span> Delete
                    </button>
                </div>
            </header>

            <div class="card-item-grid">
                <!-- Interactive Attribute Controls (Simultaneously generated) -->
                <div class="card-attr-controls" aria-label="Attribute settings">
                    <h4 class="controls-heading">⚙️ Interactive Attribute Settings:</h4>
                    
                    <div class="attr-form-grid">
                        <div class="form-group">
                            <label for="attr-name-${item.id}">
                                <code>name</code> (field name):
                            </label>
                            <input type="text" id="attr-name-${item.id}" class="form-control attr-input"
                                   data-prop="name" value="${escapeHtml(item.name)}" placeholder="e.g. feedback_text">
                        </div>

                        <div class="form-group-row">
                            <div class="form-group">
                                <label for="attr-rows-${item.id}">
                                    <code>rows</code> (line height):
                                </label>
                                <input type="number" id="attr-rows-${item.id}" class="form-control attr-input"
                                       data-prop="rows" min="1" max="50" value="${item.rows}">
                            </div>

                            <div class="form-group">
                                <label for="attr-cols-${item.id}">
                                    <code>cols</code> (column width):
                                </label>
                                <input type="number" id="attr-cols-${item.id}" class="form-control attr-input"
                                       data-prop="cols" min="5" max="150" value="${item.cols}">
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="attr-placeholder-${item.id}">
                                <code>placeholder</code> (hint text):
                            </label>
                            <input type="text" id="attr-placeholder-${item.id}" class="form-control attr-input"
                                   data-prop="placeholder" value="${escapeHtml(item.placeholder)}" placeholder="Hint inside field...">
                        </div>

                        <div class="form-group-row">
                            <div class="form-group">
                                <label for="attr-maxlength-${item.id}">
                                    <code>maxlength</code> (char limit):
                                </label>
                                <input type="number" id="attr-maxlength-${item.id}" class="form-control attr-input"
                                       data-prop="maxlength" min="0" placeholder="No limit"
                                       value="${item.maxlength !== null && item.maxlength !== undefined ? item.maxlength : ''}">
                            </div>

                            <div class="form-group">
                                <label for="attr-wrap-${item.id}">
                                    <code>wrap</code> (word wrapping):
                                </label>
                                <select id="attr-wrap-${item.id}" class="form-control attr-input" data-prop="wrap">
                                    <option value="soft" ${item.wrap === 'soft' ? 'selected' : ''}>soft (soft display wrap)</option>
                                    <option value="hard" ${item.wrap === 'hard' ? 'selected' : ''}>hard (hard wrap with \\n)</option>
                                    <option value="off" ${item.wrap === 'off' ? 'selected' : ''}>off (no wrap)</option>
                                </select>
                            </div>
                        </div>

                        <div class="form-group checkbox-group">
                            <label class="custom-checkbox-label" for="attr-readonly-${item.id}">
                                <input type="checkbox" id="attr-readonly-${item.id}" class="attr-input"
                                       data-prop="readonly" ${item.readonly ? 'checked' : ''}>
                                <span class="checkbox-custom"></span>
                                <span class="checkbox-text"><code>readonly</code> (read-only mode)</span>
                            </label>
                        </div>
                    </div>
                </div>

                <!-- Live Generated <textarea> Preview -->
                <div class="card-preview-area" aria-label="Element preview">
                    <div class="preview-header">
                        <h4 class="controls-heading">👁️ Live Element Preview:</h4>
                        <div class="char-counter" id="char-counter-${item.id}">
                            Characters: <strong class="char-current">${(item.value || '').length}</strong>
                            ${item.maxlength ? ` / <span class="char-max">${item.maxlength}</span>` : ''}
                        </div>
                    </div>

                    <div class="textarea-interactive-wrapper">
                        <!-- THE ACTUAL GENERATED TEXTAREA -->
                        <textarea id="target-textarea-${item.id}"
                                  class="target-generated-textarea ${item.readonly ? 'is-readonly' : ''}"
                                  name="${escapeHtml(item.name)}"
                                  rows="${item.rows}"
                                  cols="${item.cols}"
                                  placeholder="${escapeHtml(item.placeholder)}"
                                  ${item.maxlength ? `maxlength="${item.maxlength}"` : ''}
                                  wrap="${escapeHtml(item.wrap)}"
                                  ${item.readonly ? 'readonly' : ''}>${escapeHtml(item.value || '')}</textarea>
                    </div>

                    <!-- Live Code Snippet Display -->
                    <div class="markup-snippet-wrapper">
                        <div class="snippet-header">
                            <span class="snippet-label">Generated HTML Code (updates interactively):</span>
                            <button type="button" class="btn-copy-code" data-action="copy" title="Copy HTML code">
                                📋 Copy
                            </button>
                        </div>
                        <pre class="snippet-pre"><code class="snippet-code" id="snippet-${item.id}">${escapeHtml(buildHtmlSnippet(item))}</code></pre>
                    </div>
                </div>
            </div>
        `;

        // Wire up reactive inputs
        const targetTextarea = card.querySelector(`#target-textarea-${item.id}`);
        const snippetEl = card.querySelector(`#snippet-${item.id}`);
        const tagBadge = card.querySelector('.badge-tag');
        const charCounterEl = card.querySelector(`#char-counter-${item.id}`);
        const charCurrent = charCounterEl.querySelector('.char-current');

        function updateCharCounter() {
            const currentLen = targetTextarea.value.length;
            charCurrent.textContent = currentLen;
            const max = item.maxlength;
            if (max !== null && max !== undefined && max !== '' && !isNaN(max)) {
                charCounterEl.innerHTML = `Characters: <strong class="char-current">${currentLen}</strong> / <span class="char-max">${max}</span>`;
            } else {
                charCounterEl.innerHTML = `Characters: <strong class="char-current">${currentLen}</strong>`;
            }
        }

        // Handle attribute inputs
        const attrInputs = card.querySelectorAll('.attr-input');
        attrInputs.forEach(input => {
            const handler = () => {
                const prop = input.getAttribute('data-prop');
                if (!prop) return;

                if (prop === 'readonly') {
                    item.readonly = input.checked;
                    targetTextarea.readOnly = input.checked;
                    if (input.checked) {
                        targetTextarea.setAttribute('readonly', 'readonly');
                        targetTextarea.classList.add('is-readonly');
                    } else {
                        targetTextarea.removeAttribute('readonly');
                        targetTextarea.classList.remove('is-readonly');
                    }
                } else if (prop === 'rows') {
                    const val = parseInt(input.value, 10) || 2;
                    item.rows = val;
                    targetTextarea.rows = val;
                    targetTextarea.setAttribute('rows', val);
                } else if (prop === 'cols') {
                    const val = parseInt(input.value, 10) || 10;
                    item.cols = val;
                    targetTextarea.cols = val;
                    targetTextarea.setAttribute('cols', val);
                } else if (prop === 'maxlength') {
                    const val = input.value.trim();
                    if (val === '' || isNaN(val) || parseInt(val, 10) < 0) {
                        item.maxlength = null;
                        targetTextarea.removeAttribute('maxlength');
                    } else {
                        const num = parseInt(val, 10);
                        item.maxlength = num;
                        targetTextarea.setAttribute('maxlength', num);
                    }
                    updateCharCounter();
                } else if (prop === 'name') {
                    const val = input.value.trim();
                    item.name = val;
                    targetTextarea.name = val;
                    targetTextarea.setAttribute('name', val);
                    tagBadge.textContent = `<textarea name="${val}">`;
                } else if (prop === 'placeholder') {
                    item.placeholder = input.value;
                    targetTextarea.placeholder = input.value;
                    targetTextarea.setAttribute('placeholder', input.value);
                } else if (prop === 'wrap') {
                    item.wrap = input.value;
                    targetTextarea.setAttribute('wrap', input.value);
                    targetTextarea.wrap = input.value;
                }

                // Update Code Snippet
                snippetEl.innerHTML = escapeHtml(buildHtmlSnippet(item));
                saveState();
            };

            input.addEventListener('input', handler);
            input.addEventListener('change', handler);
        });

        // Handle typing inside generated textarea
        targetTextarea.addEventListener('input', () => {
            item.value = targetTextarea.value;
            updateCharCounter();
            snippetEl.innerHTML = escapeHtml(buildHtmlSnippet(item));
            saveState();
        });

        // Handle item deletion
        const deleteBtn = card.querySelector('[data-action="delete"]');
        deleteBtn.addEventListener('click', () => {
            deleteItem(item.id);
        });

        // Handle copy code button
        const copyBtn = card.querySelector('[data-action="copy"]');
        copyBtn.addEventListener('click', () => {
            const codeText = buildHtmlSnippet(item);
            navigator.clipboard.writeText(codeText).then(() => {
                const orig = copyBtn.innerHTML;
                copyBtn.innerHTML = '✅ Copied!';
                copyBtn.classList.add('copied');
                setTimeout(() => {
                    copyBtn.innerHTML = orig;
                    copyBtn.classList.remove('copied');
                }, 1500);
            }).catch(() => {
                // Fallback copy
                const temp = document.createElement('textarea');
                temp.value = codeText;
                document.body.appendChild(temp);
                temp.select();
                document.execCommand('copy');
                document.body.removeChild(temp);
                copyBtn.innerHTML = '✅ Copied!';
                setTimeout(() => {
                    copyBtn.innerHTML = '📋 Copy';
                }, 1500);
            });
        });

        return card;
    }

    /**
     * Delete an item by ID
     */
    function deleteItem(id) {
        const targetCard = document.getElementById(`card-${id}`);
        if (targetCard) {
            targetCard.classList.add('is-removing');
            setTimeout(() => {
                items = items.filter(it => it.id !== id);
                saveState();
                renderAll();
            }, 250);
        } else {
            items = items.filter(it => it.id !== id);
            saveState();
            renderAll();
        }
    }

    /**
     * Clear all generated items
     */
    function clearAllItems() {
        if (!items.length) return;
        if (confirm(`Delete all generated textarea elements (${items.length} items)?`)) {
            items = [];
            saveState();
            renderAll();
        }
    }

    /**
     * Add a new item to the collection
     */
    function addNewItem() {
        const newItem = createNewItemData();
        items.push(newItem);
        saveState();
        renderAll();

        // Smoothly scroll to the newly created element
        setTimeout(() => {
            const cardEl = document.getElementById(`card-${newItem.id}`);
            if (cardEl) {
                cardEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                const nameInput = cardEl.querySelector('.attr-input');
                if (nameInput) nameInput.focus();
            }
        }, 100);
    }

    /**
     * Handle main toggle checkbox change
     */
    function handleTriggerToggle() {
        if (triggerCheckbox.checked) {
            // Checkbox checked -> Generate at least one item if none exist
            if (items.length === 0) {
                addNewItem();
            } else {
                renderAll();
            }
        } else {
            // Checkbox unchecked -> confirm or remove all
            if (items.length > 0) {
                const confirmed = confirm('Turning off the toggle will remove all generated textarea elements from the page. Continue?');
                if (confirmed) {
                    items = [];
                    saveState();
                    renderAll();
                } else {
                    // Re-check the box if user canceled
                    triggerCheckbox.checked = true;
                }
            } else {
                renderAll();
            }
        }
    }

    /**
     * Render entire UI based on items state
     */
    function renderAll() {
        container.innerHTML = '';

        if (items.length === 0) {
            emptyState.style.display = 'block';
            actionsBar.style.display = 'none';
            triggerCheckbox.checked = false;
            countBadge.textContent = '0';
        } else {
            emptyState.style.display = 'none';
            actionsBar.style.display = 'flex';
            triggerCheckbox.checked = true;
            countBadge.textContent = items.length;

            items.forEach((item, index) => {
                const card = renderCard(item, index);
                container.appendChild(card);
            });
        }
    }

    /**
     * Initialize Task 4 module
     */
    function init() {
        triggerCheckbox = document.getElementById('generatorTriggerCheckbox');
        actionsBar = document.getElementById('generatorActionsBar');
        addMoreBtn = document.getElementById('addMoreTextareaBtn');
        clearAllBtn = document.getElementById('clearAllTextareasBtn');
        emptyState = document.getElementById('generatorEmptyState');
        container = document.getElementById('textareaItemsContainer');
        countBadge = document.getElementById('textareasCountBadge');

        if (!triggerCheckbox || !container) {
            return; // Not on JS Lab page
        }

        // Load saved state
        loadState();

        // Event Listeners
        triggerCheckbox.addEventListener('change', handleTriggerToggle);
        addMoreBtn.addEventListener('click', addNewItem);
        clearAllBtn.addEventListener('click', clearAllItems);

        // Initial render
        renderAll();
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
