/**
 * Pastry Shop — LR3 JS Lab: Task 4 (Variant 24)
 * Dynamic Form Element Generator (<textarea>)
 *
 * Requirements:
 * 1. Checkbox triggers dynamic generation of the form element (<textarea>).
 * 2. Simultaneous generation of interactive attribute settings:
 *    - name, rows, cols, placeholder, maxlength, wrap, readonly.
 * 3. Reactive binding: changes in settings immediately apply to the <textarea>.
 * 4. Multiple elements can be added.
 * 5. Deletion of individual elements.
 * 6. Persistent state in localStorage across page reloads.
 */

(function() {
    'use strict';

    const STORAGE_KEY = 'pastry_generated_textareas';
    let items = [];

    // DOM Elements
    let triggerCheckbox = null;
    let actionsBar = null;
    let addMoreBtn = null;
    let clearAllBtn = null;
    let emptyState = null;
    let container = null;
    let countBadge = null;

    function loadState() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            items = raw ? JSON.parse(raw) : [];
        } catch (e) {
            items = [];
        }
    }

    function saveState() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
        } catch (e) {
            console.error('Failed to save to localStorage:', e);
        }
    }

    function createItemData() {
        const idx = items.length + 1;
        return {
            id: 'ta_' + Date.now() + '_' + Math.floor(Math.random() * 1000),
            name: 'feedback_msg_' + idx,
            rows: 4,
            cols: 35,
            placeholder: 'Type your confectionery order note here...',
            maxlength: 200,
            wrap: 'soft',
            readonly: false,
            value: ''
        };
    }

    function renderAll() {
        if (!container) return;
        container.innerHTML = '';

        const hasItems = items.length > 0;
        if (triggerCheckbox) triggerCheckbox.checked = hasItems;
        if (emptyState) emptyState.style.display = hasItems ? 'none' : 'block';
        if (actionsBar) actionsBar.style.display = hasItems ? 'flex' : 'none';
        if (countBadge) countBadge.textContent = items.length;

        items.forEach(function(item, index) {
            const card = document.createElement('article');
            card.className = 'textarea-item-card card-box';

            // 1. Header with Counter and Delete Button
            const header = document.createElement('header');
            header.className = 'card-item-header';
            header.innerHTML = `
                <div class="card-item-title-group">
                    <span class="card-item-counter">#${index + 1}</span>
                    <h3 class="card-item-title">&lt;textarea&gt; Form Element</h3>
                </div>
            `;

            const delBtn = document.createElement('button');
            delBtn.type = 'button';
            delBtn.className = 'btn btn-sm btn-delete-item';
            delBtn.innerHTML = '🗑️ Delete';
            delBtn.addEventListener('click', function() {
                items.splice(index, 1);
                saveState();
                renderAll();
            });
            header.appendChild(delBtn);
            card.appendChild(header);

            // 2. Card Body: Attribute Settings + Live Textarea
            const bodyGrid = document.createElement('div');
            bodyGrid.className = 'card-item-grid';

            // Attribute Controls
            const controls = document.createElement('div');
            controls.className = 'card-attr-controls';
            controls.innerHTML = `
                <h4 class="controls-heading">⚙️ Interactive Attribute Settings:</h4>
                <div class="attr-form-grid">
                    <div class="form-group">
                        <label><code>name</code>:</label>
                        <input type="text" class="form-control" data-prop="name" value="${item.name}">
                    </div>
                    <div class="form-group-row">
                        <div class="form-group">
                            <label><code>rows</code>:</label>
                            <input type="number" class="form-control" data-prop="rows" min="1" max="30" value="${item.rows}">
                        </div>
                        <div class="form-group">
                            <label><code>cols</code>:</label>
                            <input type="number" class="form-control" data-prop="cols" min="5" max="100" value="${item.cols}">
                        </div>
                    </div>
                    <div class="form-group">
                        <label><code>placeholder</code>:</label>
                        <input type="text" class="form-control" data-prop="placeholder" value="${item.placeholder}">
                    </div>
                    <div class="form-group-row">
                        <div class="form-group">
                            <label><code>maxlength</code>:</label>
                            <input type="number" class="form-control" data-prop="maxlength" min="0" value="${item.maxlength || ''}">
                        </div>
                        <div class="form-group">
                            <label><code>wrap</code>:</label>
                            <select class="form-control" data-prop="wrap">
                                <option value="soft" ${item.wrap === 'soft' ? 'selected' : ''}>soft</option>
                                <option value="hard" ${item.wrap === 'hard' ? 'selected' : ''}>hard</option>
                                <option value="off" ${item.wrap === 'off' ? 'selected' : ''}>off</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group checkbox-group" style="margin-top: 0.5rem;">
                        <label class="custom-checkbox-label">
                            <input type="checkbox" data-prop="readonly" ${item.readonly ? 'checked' : ''}>
                            <span class="checkbox-text"><code>readonly</code></span>
                        </label>
                    </div>
                </div>
            `;

            // Live Preview Area
            const previewArea = document.createElement('div');
            previewArea.className = 'card-preview-area';
            previewArea.innerHTML = '<h4 class="controls-heading">👁️ Live &lt;textarea&gt; Preview:</h4>';

            const textareaWrapper = document.createElement('div');
            textareaWrapper.className = 'textarea-interactive-wrapper';

            // THE REAL GENERATED TEXTAREA
            const targetTextarea = document.createElement('textarea');
            targetTextarea.className = 'target-generated-textarea';
            targetTextarea.name = item.name;
            targetTextarea.rows = item.rows;
            targetTextarea.cols = item.cols;
            targetTextarea.placeholder = item.placeholder;
            if (item.maxlength) targetTextarea.maxLength = item.maxlength;
            targetTextarea.wrap = item.wrap;
            targetTextarea.readOnly = item.readonly;
            targetTextarea.value = item.value || '';

            // User input on textarea updates item.value in localStorage
            targetTextarea.addEventListener('input', function() {
                item.value = this.value;
                saveState();
            });

            textareaWrapper.appendChild(targetTextarea);
            previewArea.appendChild(textareaWrapper);

            bodyGrid.appendChild(controls);
            bodyGrid.appendChild(previewArea);
            card.appendChild(bodyGrid);

            // Reactive updates when changing attribute inputs
            const inputs = controls.querySelectorAll('input, select');
            inputs.forEach(function(input) {
                input.addEventListener('input', function() {
                    const prop = this.getAttribute('data-prop');
                    if (prop === 'name') {
                        item.name = this.value;
                        targetTextarea.name = this.value;
                    } else if (prop === 'rows') {
                        const val = parseInt(this.value, 10) || 2;
                        item.rows = val;
                        targetTextarea.rows = val;
                    } else if (prop === 'cols') {
                        const val = parseInt(this.value, 10) || 10;
                        item.cols = val;
                        targetTextarea.cols = val;
                    } else if (prop === 'placeholder') {
                        item.placeholder = this.value;
                        targetTextarea.placeholder = this.value;
                    } else if (prop === 'maxlength') {
                        const val = parseInt(this.value, 10);
                        if (val > 0) {
                            item.maxlength = val;
                            targetTextarea.maxLength = val;
                        } else {
                            item.maxlength = null;
                            targetTextarea.removeAttribute('maxlength');
                        }
                    } else if (prop === 'wrap') {
                        item.wrap = this.value;
                        targetTextarea.wrap = this.value;
                    } else if (prop === 'readonly') {
                        item.readonly = this.checked;
                        targetTextarea.readOnly = this.checked;
                        if (this.checked) {
                            targetTextarea.classList.add('is-readonly');
                        } else {
                            targetTextarea.classList.remove('is-readonly');
                        }
                    }
                    saveState();
                });
            });

            container.appendChild(card);
        });
    }

    function init() {
        triggerCheckbox = document.getElementById('generatorTriggerCheckbox');
        actionsBar = document.getElementById('generatorActionsBar');
        addMoreBtn = document.getElementById('addMoreTextareaBtn');
        clearAllBtn = document.getElementById('clearAllTextareasBtn');
        emptyState = document.getElementById('generatorEmptyState');
        container = document.getElementById('textareaItemsContainer');
        countBadge = document.getElementById('textareasCountBadge');

        if (!triggerCheckbox || !container) return;

        loadState();
        renderAll();

        // Toggle checkbox creates or clears items
        triggerCheckbox.addEventListener('change', function() {
            if (this.checked) {
                if (items.length === 0) {
                    items.push(createItemData());
                    saveState();
                }
            } else {
                items = [];
                saveState();
            }
            renderAll();
        });

        // Add more button
        if (addMoreBtn) {
            addMoreBtn.addEventListener('click', function() {
                items.push(createItemData());
                saveState();
                renderAll();
            });
        }

        // Clear all button
        if (clearAllBtn) {
            clearAllBtn.addEventListener('click', function() {
                items = [];
                saveState();
                renderAll();
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
