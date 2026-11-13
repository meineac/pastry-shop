/**
 * Pastry Shop — LR3 JS Lab: Task 9
 * Modern Browser Web APIs Demonstration
 *
 * Implemented APIs:
 * 1. Web Speech API (SpeechSynthesis): text-to-speech with voice selection, rate/pitch sliders, and status indication.
 * 2. Geolocation API: detects user's location and calculates exact great-circle distance to the Pastry Shop (123 Baker St, London).
 * 3. Battery Status API: inspects battery charge level and charging status (with fallback if unsupported).
 *
 * Designed with clean DOM manipulation (textContent, hidden attributes), zero raw innerHTML strings.
 */

(function() {
    'use strict';

    // Bakery Coordinates: 123 Baker Street, London, UK
    const BAKERY_LAT = 51.523695;
    const BAKERY_LON = -0.157779;

    // =========================================================================
    // 1. WEB SPEECH API (SpeechSynthesis)
    // =========================================================================

    let synth = null;
    let voices = [];

    let speechText = null;
    let voiceSelect = null;
    let rateInput = null;
    let pitchInput = null;
    let rateValueDisplay = null;
    let pitchValueDisplay = null;
    let speakBtn = null;
    let stopBtn = null;
    let speechStatusBadge = null;
    let speechNotice = null;

    function initSpeechSynthesis() {
        speechText = document.getElementById('speechTextInput');
        voiceSelect = document.getElementById('speechVoiceSelect');
        rateInput = document.getElementById('speechRateInput');
        pitchInput = document.getElementById('speechPitchInput');
        rateValueDisplay = document.getElementById('speechRateVal');
        pitchValueDisplay = document.getElementById('speechPitchVal');
        speakBtn = document.getElementById('speechSpeakBtn');
        stopBtn = document.getElementById('speechStopBtn');
        speechStatusBadge = document.getElementById('speechStatusBadge');
        speechNotice = document.getElementById('speechUnsupportedNotice');

        if (!('speechSynthesis' in window)) {
            if (speechNotice) speechNotice.hidden = false;
            if (speakBtn) speakBtn.disabled = true;
            if (stopBtn) stopBtn.disabled = true;
            return;
        }

        synth = window.speechSynthesis;

        function populateVoices() {
            voices = synth.getVoices();
            if (!voiceSelect || voices.length === 0) return;

            voiceSelect.innerHTML = '';
            voices.forEach(function(voice, i) {
                const option = document.createElement('option');
                option.textContent = voice.name + ' (' + voice.lang + ')';
                if (voice.default) {
                    option.textContent += ' [Default]';
                }
                option.value = i;
                // Prefer English voices by default
                if (voice.lang.startsWith('en')) {
                    option.selected = true;
                }
                voiceSelect.appendChild(option);
            });
        }

        populateVoices();
        if (synth.onvoiceschanged !== undefined) {
            synth.onvoiceschanged = populateVoices;
        }

        if (rateInput && rateValueDisplay) {
            rateInput.addEventListener('input', function() {
                rateValueDisplay.textContent = this.value + 'x';
            });
        }

        if (pitchInput && pitchValueDisplay) {
            pitchInput.addEventListener('input', function() {
                pitchValueDisplay.textContent = this.value;
            });
        }

        if (speakBtn) {
            speakBtn.addEventListener('click', function() {
                const text = speechText ? speechText.value.trim() : '';
                if (!text) {
                    if (speechText) speechText.focus();
                    return;
                }

                // If currently speaking, cancel previous
                synth.cancel();

                const utterance = new SpeechSynthesisUtterance(text);

                if (voiceSelect && voices[voiceSelect.value]) {
                    utterance.voice = voices[voiceSelect.value];
                }

                if (rateInput) utterance.rate = parseFloat(rateInput.value) || 1.0;
                if (pitchInput) utterance.pitch = parseFloat(pitchInput.value) || 1.0;

                utterance.onstart = function() {
                    if (speechStatusBadge) {
                        speechStatusBadge.textContent = 'Speaking...';
                        speechStatusBadge.className = 'status-pill status-active';
                    }
                };

                utterance.onend = function() {
                    if (speechStatusBadge) {
                        speechStatusBadge.textContent = 'Idle';
                        speechStatusBadge.className = 'status-pill status-idle';
                    }
                };

                utterance.onerror = function() {
                    if (speechStatusBadge) {
                        speechStatusBadge.textContent = 'Error';
                        speechStatusBadge.className = 'status-pill status-error';
                    }
                };

                synth.speak(utterance);
            });
        }

        if (stopBtn) {
            stopBtn.addEventListener('click', function() {
                if (synth) {
                    synth.cancel();
                    if (speechStatusBadge) {
                        speechStatusBadge.textContent = 'Stopped';
                        speechStatusBadge.className = 'status-pill status-idle';
                    }
                }
            });
        }
    }


    // =========================================================================
    // 2. GEOLOCATION API & DISTANCE CALCULATION
    // =========================================================================

    let locateBtn = null;
    let geoResultCard = null;
    let geoErrorBox = null;
    let geoLat = null;
    let geoLon = null;
    let geoAccuracy = null;
    let geoDistance = null;

    /**
     * Great-Circle Haversine Formula (returns distance in kilometers)
     */
    function calculateHaversineDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Earth's mean radius in km
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;

        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                  Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                  Math.sin(dLon / 2) * Math.sin(dLon / 2);

        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return Number((R * c).toFixed(1));
    }

    function initGeolocation() {
        locateBtn = document.getElementById('geoLocateBtn');
        geoResultCard = document.getElementById('geoResultCard');
        geoErrorBox = document.getElementById('geoErrorBox');
        geoLat = document.getElementById('geoLatVal');
        geoLon = document.getElementById('geoLonVal');
        geoAccuracy = document.getElementById('geoAccuracyVal');
        geoDistance = document.getElementById('geoDistanceVal');

        if (!locateBtn) return;

        locateBtn.addEventListener('click', function() {
            if (!('geolocation' in navigator)) {
                if (geoErrorBox) {
                    geoErrorBox.textContent = 'Geolocation API is not supported by your current browser.';
                    geoErrorBox.hidden = false;
                }
                return;
            }

            if (geoErrorBox) geoErrorBox.hidden = true;
            locateBtn.disabled = true;
            locateBtn.textContent = '⏳ Acquiring coordinates...';

            navigator.geolocation.getCurrentPosition(
                // Success callback
                function(position) {
                    locateBtn.disabled = false;
                    locateBtn.textContent = '📍 Locate Me & Calculate Distance';

                    const userLat = position.coords.latitude;
                    const userLon = position.coords.longitude;
                    const accuracy = Math.round(position.coords.accuracy);

                    const distanceKm = calculateHaversineDistance(userLat, userLon, BAKERY_LAT, BAKERY_LON);

                    if (geoLat) geoLat.textContent = userLat.toFixed(5) + '°';
                    if (geoLon) geoLon.textContent = userLon.toFixed(5) + '°';
                    if (geoAccuracy) geoAccuracy.textContent = '± ' + accuracy + ' meters';
                    if (geoDistance) geoDistance.textContent = distanceKm.toLocaleString() + ' km';

                    if (geoResultCard) {
                        geoResultCard.hidden = false;
                        geoResultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }
                },
                // Error callback
                function(error) {
                    locateBtn.disabled = false;
                    locateBtn.textContent = '📍 Locate Me & Calculate Distance';

                    let errorMsg = 'Failed to retrieve location.';
                    switch (error.code) {
                        case error.PERMISSION_DENIED:
                            errorMsg = 'Permission denied. Please allow location access in your browser.';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMsg = 'Location information is currently unavailable.';
                            break;
                        case error.TIMEOUT:
                            errorMsg = 'Location request timed out. Please try again.';
                            break;
                    }

                    if (geoErrorBox) {
                        geoErrorBox.textContent = errorMsg;
                        geoErrorBox.hidden = false;
                    }
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 60000
                }
            );
        });
    }


    // =========================================================================
    // 3. BATTERY STATUS API (Bonus)
    // =========================================================================

    function initBatteryStatus() {
        const batteryFill = document.getElementById('batteryFillBar');
        const batteryPct = document.getElementById('batteryPctVal');
        const batteryStatus = document.getElementById('batteryChargingStatus');
        const batteryBox = document.getElementById('batteryCardBox');
        const batteryUnsupported = document.getElementById('batteryUnsupportedNotice');

        if (!('getBattery' in navigator)) {
            if (batteryUnsupported) batteryUnsupported.hidden = false;
            if (batteryBox) batteryBox.hidden = true;
            return;
        }

        navigator.getBattery().then(function(battery) {
            function updateBatteryUI() {
                const pct = Math.round(battery.level * 100);
                if (batteryPct) batteryPct.textContent = pct + '%';
                if (batteryFill) {
                    batteryFill.style.width = pct + '%';
                    if (pct <= 20) {
                        batteryFill.style.backgroundColor = '#e74c3c';
                    } else if (pct <= 50) {
                        batteryFill.style.backgroundColor = '#f39c12';
                    } else {
                        batteryFill.style.backgroundColor = '#27ae60';
                    }
                }
                if (batteryStatus) {
                    batteryStatus.textContent = battery.charging ? '⚡ Charging' : '🔋 On Battery';
                }
            }

            updateBatteryUI();
            battery.addEventListener('levelchange', updateBatteryUI);
            battery.addEventListener('chargingchange', updateBatteryUI);
        }).catch(function() {
            if (batteryUnsupported) batteryUnsupported.hidden = false;
            if (batteryBox) batteryBox.hidden = true;
        });
    }


    // =========================================================================
    // INITIALIZATION
    // =========================================================================

    function init() {
        initSpeechSynthesis();
        initGeolocation();
        initBatteryStatus();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
