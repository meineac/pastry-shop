/**
 * Pastry Shop — LR3 JS Lab: Task 8 (Variant 24)
 * Object-Oriented Programming (OOP) in JavaScript: Mobile Network Subscribers
 *
 * Requirements:
 * 1. Base Class: operator, phone. Must have 5 methods (getters/setters, info).
 * 2. Derived Class: adds callsCount, totalDuration. Must have 5 methods:
 *    - getAverageDuration()
 *    - getDetailedInfo()
 *    - addFromForm(formData) - adds an object from HTML form
 *    - renderAll(container, list) - renders objects into an HTML table
 *    - renderResult(container, result) - displays algorithm result
 * 3. Two implementations:
 *    - Functional Prototypal Inheritance (function constructor + Object.create)
 *    - Modern ES6 syntax (class + extends + super)
 * 4. Algorithm (Variant 24):
 *    Find all subscribers who had the highest number of calls inside the network
 *    with their lowest average duration.
 */

(function() {
    'use strict';

    // =========================================================================
    // PARADIGM 1: Functional Prototypal Inheritance
    // =========================================================================

    /**
     * Base Constructor: AbonentProto
     */
    function AbonentProto(operator, phone) {
        this._operator = String(operator || '').trim();
        this._phone = String(phone || '').trim();
    }

    // 5 Methods on Base Prototype
    AbonentProto.prototype.getOperator = function() { return this._operator; };
    AbonentProto.prototype.setOperator = function(op) { this._operator = String(op || '').trim(); };
    AbonentProto.prototype.getPhone = function() { return this._phone; };
    AbonentProto.prototype.setPhone = function(ph) { this._phone = String(ph || '').trim(); };
    AbonentProto.prototype.getBaseInfo = function() {
        return this._operator + ' (' + this._phone + ')';
    };

    /**
     * Derived Constructor: CellularAbonentProto
     */
    function CellularAbonentProto(operator, phone, callsCount, totalDuration) {
        // Call base constructor with current context
        AbonentProto.call(this, operator, phone);

        this._callsCount = Math.max(0, parseInt(callsCount, 10) || 0);
        this._totalDuration = Math.max(0, parseFloat(totalDuration) || 0);
    }

    // Prototypal inheritance setup
    CellularAbonentProto.prototype = Object.create(AbonentProto.prototype);
    CellularAbonentProto.prototype.constructor = CellularAbonentProto;

    // 5 Methods on Derived Prototype
    CellularAbonentProto.prototype.getCallsCount = function() { return this._callsCount; };
    CellularAbonentProto.prototype.getTotalDuration = function() { return this._totalDuration; };
    CellularAbonentProto.prototype.getAverageDuration = function() {
        if (this._callsCount === 0) return 0;
        return Number((this._totalDuration / this._callsCount).toFixed(2));
    };
    CellularAbonentProto.prototype.getDetailedInfo = function() {
        return this.getBaseInfo() + ' — Calls: ' + this._callsCount +
               ', Duration: ' + this._totalDuration + ' min (Avg: ' +
               this.getAverageDuration() + ' min/call)';
    };

    // Static Method: Add object from HTML form components
    CellularAbonentProto.addFromForm = function(formElement) {
        const operator = formElement.querySelector('[name="operator"]').value;
        const phone = formElement.querySelector('[name="phone"]').value;
        const callsCount = formElement.querySelector('[name="callsCount"]').value;
        const totalDuration = formElement.querySelector('[name="totalDuration"]').value;
        return new CellularAbonentProto(operator, phone, callsCount, totalDuration);
    };

    // Static Method: Render array of subscribers to HTML table via standard DOM API
    CellularAbonentProto.renderAll = function(tbodyElement, subscribersList, onDeleteCallback) {
        if (!tbodyElement) return;

        tbodyElement.innerHTML = ''; // Clear rows
        const table = document.getElementById('subscribersTable');
        const emptyMsg = document.getElementById('subscribersEmptyMessage');

        if (!subscribersList || subscribersList.length === 0) {
            if (table) table.hidden = true;
            if (emptyMsg) emptyMsg.hidden = false;
            return;
        }

        if (table) table.hidden = false;
        if (emptyMsg) emptyMsg.hidden = true;

        subscribersList.forEach(function(sub, idx) {
            const tr = tbodyElement.insertRow();

            // #
            const tdNum = tr.insertCell();
            tdNum.textContent = idx + 1;

            // Operator Badge
            const tdOp = tr.insertCell();
            const opSpan = document.createElement('span');
            opSpan.className = 'operator-badge operator-' + sub.getOperator().toLowerCase();
            opSpan.textContent = sub.getOperator();
            tdOp.appendChild(opSpan);

            // Phone Code
            const tdPhone = tr.insertCell();
            const codeEl = document.createElement('code');
            codeEl.textContent = sub.getPhone();
            tdPhone.appendChild(codeEl);

            // Calls Count Pill
            const tdCalls = tr.insertCell();
            const pill = document.createElement('span');
            pill.className = 'calls-count-pill';
            pill.textContent = sub.getCallsCount();
            tdCalls.appendChild(pill);

            // Total Duration
            const tdDuration = tr.insertCell();
            tdDuration.textContent = sub.getTotalDuration() + ' min';

            // Average Duration
            const tdAvg = tr.insertCell();
            const avgStrong = document.createElement('strong');
            avgStrong.textContent = sub.getAverageDuration();
            tdAvg.appendChild(avgStrong);
            tdAvg.appendChild(document.createTextNode(' min/call'));

            // Delete Action Button
            const tdAction = tr.insertCell();
            const delBtn = document.createElement('button');
            delBtn.type = 'button';
            delBtn.className = 'btn-delete-subscriber';
            delBtn.title = 'Delete subscriber';
            delBtn.textContent = '×';
            delBtn.addEventListener('click', function() {
                if (typeof onDeleteCallback === 'function') {
                    onDeleteCallback(idx);
                }
            });
            tdAction.appendChild(delBtn);
        });
    };

    // Static Method: Algorithm (Variant 24)
    CellularAbonentProto.findBest = function(subscribersList) {
        if (!subscribersList || subscribersList.length === 0) return [];

        let maxCalls = -1;
        subscribersList.forEach(function(s) {
            if (s.getCallsCount() > maxCalls) {
                maxCalls = s.getCallsCount();
            }
        });

        const topCallers = subscribersList.filter(function(s) {
            return s.getCallsCount() === maxCalls;
        });

        let minAvg = Infinity;
        topCallers.forEach(function(s) {
            const avg = s.getAverageDuration();
            if (avg < minAvg) {
                minAvg = avg;
            }
        });

        return topCallers.filter(function(s) {
            return s.getAverageDuration() === minAvg;
        });
    };

    // Static Method: Render Algorithm Results to DOM
    CellularAbonentProto.renderResult = function(container, winnersList, paradigmLabel) {
        if (!container) return;

        if (!winnersList || winnersList.length === 0) {
            container.hidden = true;
            return;
        }

        const maxCalls = winnersList[0].getCallsCount();
        const minAvg = winnersList[0].getAverageDuration();

        document.getElementById('winnerArchitectureBadge').textContent = paradigmLabel;
        document.getElementById('winnerCriteriaCalls').textContent = maxCalls;
        document.getElementById('winnerCriteriaAvg').textContent = minAvg;

        const grid = document.getElementById('winnersGridContainer');
        grid.innerHTML = ''; // Clear previous winners

        winnersList.forEach(function(s) {
            const card = document.createElement('div');
            card.className = 'winner-card';

            const header = document.createElement('div');
            header.className = 'winner-header';

            const opBadge = document.createElement('span');
            opBadge.className = 'operator-badge operator-' + s.getOperator().toLowerCase();
            opBadge.textContent = s.getOperator();

            const phoneSpan = document.createElement('span');
            phoneSpan.className = 'winner-phone';
            phoneSpan.textContent = s.getPhone();

            header.appendChild(opBadge);
            header.appendChild(phoneSpan);

            const stats = document.createElement('div');
            stats.className = 'winner-stats';

            function createStatBox(lbl, val, highlight) {
                const box = document.createElement('div');
                box.className = 'winner-stat';
                const labelEl = document.createElement('span');
                labelEl.className = 'stat-lbl';
                labelEl.textContent = lbl;
                const valEl = document.createElement('span');
                valEl.className = 'stat-num' + (highlight ? ' highlight-avg' : '');
                valEl.textContent = val;
                box.appendChild(labelEl);
                box.appendChild(valEl);
                return box;
            }

            stats.appendChild(createStatBox('In-Network Calls', s.getCallsCount(), false));
            stats.appendChild(createStatBox('Total Duration', s.getTotalDuration() + ' min', false));
            stats.appendChild(createStatBox('Avg Duration', s.getAverageDuration() + ' min/call', true));

            card.appendChild(header);
            card.appendChild(stats);
            grid.appendChild(card);
        });

        container.hidden = false;
        container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    };


    // =========================================================================
    // PARADIGM 2: Modern ES6 Classes
    // =========================================================================

    /**
     * Base Class: AbonentClass
     */
    class AbonentClass {
        constructor(operator, phone) {
            this._operator = String(operator || '').trim();
            this._phone = String(phone || '').trim();
        }

        getOperator() { return this._operator; }
        setOperator(op) { this._operator = String(op || '').trim(); }
        getPhone() { return this._phone; }
        setPhone(ph) { this._phone = String(ph || '').trim(); }
        getBaseInfo() { return `${this._operator} (${this._phone})`; }
    }

    /**
     * Derived Class: CellularAbonentClass
     */
    class CellularAbonentClass extends AbonentClass {
        constructor(operator, phone, callsCount, totalDuration) {
            super(operator, phone);
            this._callsCount = Math.max(0, parseInt(callsCount, 10) || 0);
            this._totalDuration = Math.max(0, parseFloat(totalDuration) || 0);
        }

        getCallsCount() { return this._callsCount; }
        getTotalDuration() { return this._totalDuration; }
        getAverageDuration() {
            if (this._callsCount === 0) return 0;
            return Number((this._totalDuration / this._callsCount).toFixed(2));
        }
        getDetailedInfo() {
            return `${this.getBaseInfo()} — Calls: ${this._callsCount}, Total: ${this._totalDuration} min (Avg: ${this.getAverageDuration()} min/call)`;
        }

        static addFromForm(formElement) {
            const operator = formElement.querySelector('[name="operator"]').value;
            const phone = formElement.querySelector('[name="phone"]').value;
            const callsCount = formElement.querySelector('[name="callsCount"]').value;
            const totalDuration = formElement.querySelector('[name="totalDuration"]').value;
            return new CellularAbonentClass(operator, phone, callsCount, totalDuration);
        }

        static renderAll(tbodyElement, list, onDelete) {
            CellularAbonentProto.renderAll(tbodyElement, list, onDelete);
        }

        static findBest(list) {
            return CellularAbonentProto.findBest(list);
        }

        static renderResult(container, winners, label) {
            CellularAbonentProto.renderResult(container, winners, label);
        }
    }


    // =========================================================================
    // CONTROLLER & DATA STATE
    // =========================================================================

    const DEFAULT_DATA = [
        { operator: 'A1', phone: '+375 (29) 111-22-33', callsCount: 180, totalDuration: 360 }, // avg 2.0
        { operator: 'MTS', phone: '+375 (29) 222-33-44', callsCount: 240, totalDuration: 600 }, // avg 2.5
        { operator: 'life:)', phone: '+375 (25) 333-44-55', callsCount: 240, totalDuration: 432 }, // avg 1.8 <-- WINNER!
        { operator: 'A1', phone: '+375 (44) 444-55-66', callsCount: 95, totalDuration: 190 },  // avg 2.0
        { operator: 'MTS', phone: '+375 (33) 555-66-77', callsCount: 210, totalDuration: 378 }, // avg 1.8
        { operator: 'life:)', phone: '+375 (25) 666-77-88', callsCount: 150, totalDuration: 450 }  // avg 3.0
    ];

    let activeParadigm = 'es6';
    let subscribers = [];

    let form = null;
    let tableBody = null;
    let resultContainer = null;
    let calcBtn = null;
    let resetDataBtn = null;
    let paradigmRadios = null;
    let currentModeBadge = null;
    let countDisplay = null;

    function instantiateSubscribers(dataList) {
        if (activeParadigm === 'proto') {
            return dataList.map(function(d) {
                return new CellularAbonentProto(d.operator, d.phone, d.callsCount, d.totalDuration);
            });
        } else {
            return dataList.map(function(d) {
                return new CellularAbonentClass(d.operator, d.phone, d.callsCount, d.totalDuration);
            });
        }
    }

    function refreshView() {
        const onDelete = function(idx) {
            subscribers.splice(idx, 1);
            refreshView();
            if (resultContainer) resultContainer.hidden = true;
        };

        if (activeParadigm === 'proto') {
            CellularAbonentProto.renderAll(tableBody, subscribers, onDelete);
        } else {
            CellularAbonentClass.renderAll(tableBody, subscribers, onDelete);
        }

        if (countDisplay) {
            countDisplay.textContent = subscribers.length;
        }

        if (currentModeBadge) {
            currentModeBadge.textContent = activeParadigm === 'proto'
                ? 'Prototype Inheritance (function & Object.create)'
                : 'ES6 Syntax (class & extends)';
        }
    }

    function handleFormSubmit(e) {
        e.preventDefault();
        const phoneInput = form.querySelector('[name="phone"]');
        if (!phoneInput.value.trim()) {
            phoneInput.focus();
            return;
        }

        let newSub;
        if (activeParadigm === 'proto') {
            newSub = CellularAbonentProto.addFromForm(form);
        } else {
            newSub = CellularAbonentClass.addFromForm(form);
        }

        subscribers.push(newSub);
        refreshView();

        phoneInput.value = '';
        if (resultContainer) resultContainer.hidden = true;
    }

    function handleCalculate() {
        const paradigmLabel = activeParadigm === 'proto'
            ? 'Functional Prototype (CellularAbonentProto)'
            : 'Modern ES6 Class (CellularAbonentClass)';

        let winners;
        if (activeParadigm === 'proto') {
            winners = CellularAbonentProto.findBest(subscribers);
            CellularAbonentProto.renderResult(resultContainer, winners, paradigmLabel);
        } else {
            winners = CellularAbonentClass.findBest(subscribers);
            CellularAbonentClass.renderResult(resultContainer, winners, paradigmLabel);
        }
    }

    function handleResetData() {
        subscribers = instantiateSubscribers(DEFAULT_DATA);
        refreshView();
        if (resultContainer) resultContainer.hidden = true;
    }

    function handleParadigmChange(e) {
        activeParadigm = e.target.value;
        const plain = subscribers.map(function(s) {
            return {
                operator: s.getOperator(),
                phone: s.getPhone(),
                callsCount: s.getCallsCount(),
                totalDuration: s.getTotalDuration()
            };
        });
        subscribers = instantiateSubscribers(plain);
        refreshView();
        if (resultContainer && !resultContainer.hidden) {
            handleCalculate();
        }
    }

    function init() {
        form = document.getElementById('addSubscriberForm');
        tableBody = document.getElementById('subscribersTableBody');
        resultContainer = document.getElementById('oopResultContainer');
        calcBtn = document.getElementById('findBestSubscribersBtn');
        resetDataBtn = document.getElementById('resetSubscribersBtn');
        paradigmRadios = document.querySelectorAll('input[name="oop_paradigm"]');
        currentModeBadge = document.getElementById('currentOopModeBadge');
        countDisplay = document.getElementById('subscribersCountDisplay');

        if (!form || !tableBody) return;

        subscribers = instantiateSubscribers(DEFAULT_DATA);
        refreshView();

        form.addEventListener('submit', handleFormSubmit);
        if (calcBtn) calcBtn.addEventListener('click', handleCalculate);
        if (resetDataBtn) resetDataBtn.addEventListener('click', handleResetData);
        if (paradigmRadios) {
            paradigmRadios.forEach(function(r) { r.addEventListener('change', handleParadigmChange); });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
