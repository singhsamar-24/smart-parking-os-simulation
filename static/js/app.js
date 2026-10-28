/**
 * NEXUS-PARK // Commercial Parking Management Platform & OS Academic Lab
 * Course: Operating Systems (CCSE0303A) - Unit 2 & Unit 3
 * Team: Group 7 (NIET Greater Noida, CSE-AI)
 */

class SmartParkingApp {
  constructor() {
    this.apiBase = window.location.origin.includes('http') ? window.location.origin : 'http://localhost:8000';
    this.audioEnabled = true;
    this.audioCtx = null;
    this.activeTab = 'overview';
    this.activeOsTab = 'cpu-scheduling';
    this.state = null;
    this.pollInterval = null;
    
    // Vehicles view state
    this.vehicleSubTab = 'active'; // 'active' | 'history'
    this.vehicleSearchQuery = '';

    // Activity log stream (client-side rolling cache)
    this.activityLogs = [];

    // Pricing rules state cache
    this.pricingRules = {
      base_hourly_rate: 30,
      ev_hourly_rate: 40,
      suv_hourly_rate: 35,
      grace_period_min: 15,
      daily_maximum: 350
    };

    this.initAudio();
    this.initLiveClock();
    this.bindEvents();
    this.initVisualizers();
    this.startPolling();
  }

  /* -------------------------------------------------------------------------
   * AUDIO FEEDBACK SYSTEM (Web Audio API Synthesizer)
   * ------------------------------------------------------------------------- */
  initAudio() {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        this.audioCtx = new AudioContext();
      }
    } catch (e) {
      console.warn('Web Audio not initialized', e);
    }
  }

  playSound(type = 'click') {
    if (!this.audioEnabled || !this.audioCtx) return;
    try {
      if (this.audioCtx.state === 'suspended') {
        this.audioCtx.resume();
      }
      const now = this.audioCtx.currentTime;
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);

      if (type === 'click') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(700, now);
        osc.frequency.exponentialRampToValueAtTime(950, now + 0.04);
        gain.gain.setValueAtTime(0.06, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.04);
        osc.start(now);
        osc.stop(now + 0.04);
      } else if (type === 'success') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(523.25, now);
        osc.frequency.setValueAtTime(659.25, now + 0.07);
        osc.frequency.setValueAtTime(783.99, now + 0.14);
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
        osc.start(now);
        osc.stop(now + 0.25);
      } else if (type === 'lock') {
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(440, now);
        osc.frequency.exponentialRampToValueAtTime(220, now + 0.12);
        gain.gain.setValueAtTime(0.09, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);
        osc.start(now);
        osc.stop(now + 0.12);
      } else if (type === 'alarm') {
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(320, now);
        osc.frequency.linearRampToValueAtTime(160, now + 0.2);
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
        osc.start(now);
        osc.stop(now + 0.25);
      }
    } catch (e) {
      // Audio playback fails gracefully
    }
  }

  /* -------------------------------------------------------------------------
   * NOTIFICATIONS & ACTIVITY LOG
   * ------------------------------------------------------------------------- */
  showToast(title, message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';

    let borderColor = 'var(--color-cyan)';
    if (type === 'success') borderColor = 'var(--color-lime)';
    if (type === 'warning') borderColor = 'var(--color-amber)';
    if (type === 'error') borderColor = 'var(--color-rose)';
    toast.style.borderLeftColor = borderColor;

    toast.innerHTML = `
      <div style="flex: 1;">
        <div style="font-weight: 700; font-size: 0.82rem; color: #fff; margin-bottom: 2px;">${title}</div>
        <div style="font-size: 0.74rem; color: var(--text-muted); font-family: var(--font-mono);">${message}</div>
      </div>
      <button class="btn btn-outline btn-icon" style="width: 22px; height: 22px; font-size: 0.65rem;" onclick="this.parentElement.remove()">✕</button>
    `;

    container.appendChild(toast);
    setTimeout(() => {
      if (toast.parentElement) toast.remove();
    }, 4500);
  }

  logActivity(icon, title, desc) {
    const timeStr = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    this.activityLogs.unshift({ icon, title, desc, timeStr });
    if (this.activityLogs.length > 30) this.activityLogs.pop();
    this.renderActivityFeed();
  }

  renderActivityFeed() {
    const container = document.getElementById('overview-activity-feed');
    if (!container) return;

    if (this.activityLogs.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; color: var(--text-dim); padding: 20px; font-size: 0.75rem;">
          No operational events recorded yet today.
        </div>
      `;
      return;
    }

    container.innerHTML = this.activityLogs.map(item => `
      <div style="display: flex; align-items: flex-start; gap: 10px; padding: 8px 10px; background: rgba(14, 19, 31, 0.6); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); font-size: 0.75rem;">
        <span style="font-size: 1rem; line-height: 1;">${item.icon}</span>
        <div style="flex: 1;">
          <div style="display: flex; justify-content: space-between; align-items: baseline;">
            <strong style="color: #fff;">${item.title}</strong>
            <span style="font-size: 0.65rem; color: var(--text-dim); font-family: var(--font-mono);">${item.timeStr}</span>
          </div>
          <div style="color: var(--text-muted); margin-top: 2px; font-family: var(--font-mono); font-size: 0.7rem;">${item.desc}</div>
        </div>
      </div>
    `).join('');
  }

  /* -------------------------------------------------------------------------
   * LIVE CLOCK & FACILITY SWITCHER
   * ------------------------------------------------------------------------- */
  initLiveClock() {
    const clockEl = document.getElementById('live-server-clock');
    const update = () => {
      const now = new Date();
      const dateStr = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
      const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      if (clockEl) {
        clockEl.innerText = `${dateStr} · ${timeStr} · FACILITY ONLINE`;
      }
    };
    update();
    setInterval(update, 1000);
  }

  /* -------------------------------------------------------------------------
   * SUB-VISUALIZERS INITIALIZATION
   * ------------------------------------------------------------------------- */
  initVisualizers() {
    if (window.ThreeParkingVisualizer) {
      window.threeParking = new ThreeParkingVisualizer('three-parking-viewport');
    }
    if (window.ParkingLotVisualizer) {
      window.parkingLotViz = new ParkingLotVisualizer();
    }
    if (window.SchedulerVisualizer) {
      window.schedulerViz = new SchedulerVisualizer();
    }
    if (window.ConcurrencyVisualizer) {
      window.concurrencyViz = new ConcurrencyVisualizer();
    }
    if (window.BankersVisualizer) {
      window.bankersViz = new BankersVisualizer();
    }
    if (window.ClassicalVisualizer) {
      window.classicalViz = new ClassicalVisualizer();
    }
  }

  /* -------------------------------------------------------------------------
   * EVENT BINDING & ROUTING
   * ------------------------------------------------------------------------- */
  bindEvents() {
    // 1. Commercial Top-Level Navigation Tabs
    document.querySelectorAll('.tabs-nav-bar .tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const tabId = btn.getAttribute('data-tab');
        this.switchTab(tabId);
        this.playSound('click');
      });
    });

    // 2. Sound Toggle Button
    const soundBtn = document.getElementById('sound-toggle-btn');
    if (soundBtn) {
      soundBtn.addEventListener('click', () => {
        this.audioEnabled = !this.audioEnabled;
        soundBtn.innerHTML = this.audioEnabled ? '🔊' : '🔇';
        this.showToast('Audio System', this.audioEnabled ? 'Sound FX Enabled' : 'Sound FX Muted', 'info');
      });
    }

    // 3. Facility Switcher Dropdown
    const facSelect = document.getElementById('facility-select');
    const facSubtitle = document.getElementById('header-facility-subtitle');
    if (facSelect) {
      facSelect.addEventListener('change', (e) => {
        this.playSound('click');
        const val = e.target.value;
        if (facSubtitle) {
          if (val === 'FAC-01') facSubtitle.innerText = 'Metro Central Facility · Terminal Deck A · Sector 62';
          else if (val === 'FAC-02') facSubtitle.innerText = 'Metro Central Hub · Terminal Deck B (Simulated)';
          else if (val === 'FAC-03') facSubtitle.innerText = 'Hospital Wing Express Deck · Emergency Bay (Simulated)';
        }
        this.showToast('Facility Switched', `Switched view to ${e.target.options[e.target.selectedIndex].text}`, 'info');
      });
    }

    // 4. Academic OS Lab Modal Open / Close
    const btnOpenOsLab = document.getElementById('btn-open-os-lab');
    const btnCloseOsLab = document.getElementById('close-os-lab-modal');
    const osLabModal = document.getElementById('os-lab-modal');

    if (btnOpenOsLab && osLabModal) {
      btnOpenOsLab.addEventListener('click', () => {
        osLabModal.classList.add('active');
        this.playSound('click');
        this.refreshActiveOsTab();
      });
    }

    if (btnCloseOsLab && osLabModal) {
      btnCloseOsLab.addEventListener('click', () => {
        osLabModal.classList.remove('active');
        this.playSound('click');
      });
    }

    // Academic OS Lab Sub-Tabs
    document.querySelectorAll('.os-lab-tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const targetOsTab = btn.getAttribute('data-ostab');
        this.switchOsLabTab(targetOsTab);
        this.playSound('click');
      });
    });

    // 5. 3D Camera Presets
    const btnIso = document.getElementById('btn-3d-cam-iso');
    const btnTop = document.getElementById('btn-3d-cam-top');
    const btnGate = document.getElementById('btn-3d-cam-gate');

    if (btnIso) btnIso.addEventListener('click', () => window.threeParking?.setCameraPreset('iso'));
    if (btnTop) btnTop.addEventListener('click', () => window.threeParking?.setCameraPreset('top'));
    if (btnGate) btnGate.addEventListener('click', () => window.threeParking?.setCameraPreset('gate'));

    // 6. 3D vs 2D Schematic Toggle
    const btn3D = document.getElementById('btn-toggle-3d');
    const btnSchematic = document.getElementById('btn-toggle-schematic');
    const view3D = document.getElementById('three-parking-viewport');
    const viewSchematic = document.getElementById('schematic-viewport');
    const camGroup = document.getElementById('cam-presets-group');

    if (btn3D && btnSchematic && view3D && viewSchematic) {
      btn3D.addEventListener('click', () => {
        btn3D.style.background = 'var(--color-lime)';
        btn3D.style.color = '#000';
        btnSchematic.style.background = 'transparent';
        btnSchematic.style.color = 'var(--text-pure)';
        view3D.style.display = 'block';
        viewSchematic.style.display = 'none';
        if (camGroup) camGroup.style.display = 'flex';
        this.playSound('click');
      });

      btnSchematic.addEventListener('click', () => {
        btnSchematic.style.background = 'var(--color-lime)';
        btnSchematic.style.color = '#000';
        btn3D.style.background = 'transparent';
        btn3D.style.color = 'var(--text-pure)';
        view3D.style.display = 'none';
        viewSchematic.style.display = 'block';
        if (camGroup) camGroup.style.display = 'none';
        this.playSound('click');
        if (this.state && window.parkingLotViz) {
          window.parkingLotViz.renderSchematic(this.state.slots);
        }
      });
    }

    // 7. Overview Quick Actions
    const btnQuickEntry = document.getElementById('btn-quick-entry');
    const btnQuickExit = document.getElementById('btn-quick-exit');
    const btnQuickReserve = document.getElementById('btn-quick-reserve');
    const btnQuickSurge = document.getElementById('btn-quick-surge');

    if (btnQuickEntry) {
      btnQuickEntry.addEventListener('click', () => {
        this.switchTab('entry-exit');
        this.playSound('click');
        setTimeout(() => document.getElementById('kiosk-in-plate')?.focus(), 100);
      });
    }

    if (btnQuickExit) {
      btnQuickExit.addEventListener('click', () => {
        this.switchTab('entry-exit');
        this.playSound('click');
        setTimeout(() => document.getElementById('kiosk-out-vehicle-select')?.focus(), 100);
      });
    }

    if (btnQuickReserve) {
      btnQuickReserve.addEventListener('click', () => {
        this.openReservationModal();
        this.playSound('click');
      });
    }

    if (btnQuickSurge) {
      btnQuickSurge.addEventListener('click', () => {
        this.triggerTrafficSurge();
      });
    }

    // 8. Ingress Attendant Kiosk Handlers
    const btnRandomPlate = document.getElementById('btn-kiosk-random-plate');
    const btnSubmitEntry = document.getElementById('btn-kiosk-submit-entry');

    if (btnRandomPlate) {
      btnRandomPlate.addEventListener('click', () => {
        this.generateRandomKioskPlate();
        this.playSound('click');
      });
    }

    if (btnSubmitEntry) {
      btnSubmitEntry.addEventListener('click', () => {
        this.submitKioskEntry();
      });
    }

    // 9. Egress Attendant Kiosk Handlers
    const kioskOutSelect = document.getElementById('kiosk-out-vehicle-select');
    const btnSubmitExit = document.getElementById('btn-kiosk-submit-exit');

    if (kioskOutSelect) {
      kioskOutSelect.addEventListener('change', () => {
        this.updateEgressBillPreview();
      });
    }

    if (btnSubmitExit) {
      btnSubmitExit.addEventListener('click', () => {
        this.submitKioskExit();
      });
    }

    // 10. Vehicles Registry Sub-Tabs & Search
    const btnSubActive = document.getElementById('btn-sub-active-vehicles');
    const btnSubHistory = document.getElementById('btn-sub-history-vehicles');
    const vehiclesSearch = document.getElementById('vehicles-search-input');
    const btnVehiclesEntry = document.getElementById('btn-vehicles-entry-modal');

    if (btnSubActive && btnSubHistory) {
      btnSubActive.addEventListener('click', () => {
        this.vehicleSubTab = 'active';
        btnSubActive.style.background = 'rgba(16, 231, 97, 0.12)';
        btnSubActive.style.color = 'var(--color-lime)';
        btnSubHistory.style.background = 'transparent';
        btnSubHistory.style.color = 'var(--text-pure)';
        document.getElementById('container-active-vehicles').style.display = 'block';
        document.getElementById('container-history-vehicles').style.display = 'none';
        this.playSound('click');
        this.renderVehiclesRegistry();
      });

      btnSubHistory.addEventListener('click', () => {
        this.vehicleSubTab = 'history';
        btnSubHistory.style.background = 'rgba(16, 231, 97, 0.12)';
        btnSubHistory.style.color = 'var(--color-lime)';
        btnSubActive.style.background = 'transparent';
        btnSubActive.style.color = 'var(--text-pure)';
        document.getElementById('container-active-vehicles').style.display = 'none';
        document.getElementById('container-history-vehicles').style.display = 'block';
        this.playSound('click');
        this.renderVehiclesRegistry();
      });
    }

    if (vehiclesSearch) {
      vehiclesSearch.addEventListener('input', (e) => {
        this.vehicleSearchQuery = e.target.value.toLowerCase().trim();
        this.renderVehiclesRegistry();
      });
    }

    if (btnVehiclesEntry) {
      btnVehiclesEntry.addEventListener('click', () => {
        this.switchTab('entry-exit');
        this.playSound('click');
      });
    }

    // 11. Advance Reservations Modal & Management
    const btnOpenRes = document.getElementById('btn-open-res-modal');
    const resModal = document.getElementById('new-reservation-modal');
    const closeResModal = document.getElementById('close-res-modal');
    const btnCancelRes = document.getElementById('btn-cancel-res');
    const btnSubmitRes = document.getElementById('btn-submit-res');

    if (btnOpenRes) {
      btnOpenRes.addEventListener('click', () => {
        this.openReservationModal();
        this.playSound('click');
      });
    }

    const dismissResModal = () => {
      if (resModal) resModal.classList.remove('active');
    };

    if (closeResModal) closeResModal.addEventListener('click', dismissResModal);
    if (btnCancelRes) btnCancelRes.addEventListener('click', dismissResModal);
    if (resModal) {
      resModal.addEventListener('click', (e) => {
        if (e.target === resModal) dismissResModal();
      });
    }

    if (btnSubmitRes) {
      btnSubmitRes.addEventListener('click', () => {
        this.submitNewReservation();
      });
    }

    // 12. Tariff Pricing Rule Saving
    const btnSavePricing = document.getElementById('btn-save-pricing');
    if (btnSavePricing) {
      btnSavePricing.addEventListener('click', () => {
        this.saveTariffPricing();
      });
    }

    // 13. Reports CSV Export
    const btnExportCsv = document.getElementById('btn-export-csv');
    if (btnExportCsv) {
      btnExportCsv.addEventListener('click', () => {
        this.exportOperationalAuditCsv();
      });
    }

    // 14. Printable Receipt Modal Dismiss
    const receiptModal = document.getElementById('receipt-modal');
    const closeReceiptBtn = document.getElementById('close-receipt-modal');
    const dismissReceiptBtn = document.getElementById('btn-dismiss-receipt');

    const closeReceipt = () => {
      if (receiptModal) receiptModal.classList.remove('active');
    };

    if (closeReceiptBtn) closeReceiptBtn.addEventListener('click', closeReceipt);
    if (dismissReceiptBtn) dismissReceiptBtn.addEventListener('click', closeReceipt);
    if (receiptModal) {
      receiptModal.addEventListener('click', (e) => {
        if (e.target === receiptModal) closeReceipt();
      });
    }
  }

  /* -------------------------------------------------------------------------
   * TAB SWITCHING LOGIC
   * ------------------------------------------------------------------------- */
  switchTab(tabId) {
    this.activeTab = tabId;

    document.querySelectorAll('.tabs-nav-bar .tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
    });

    document.querySelectorAll('.tab-panel').forEach(panel => {
      panel.classList.toggle('active', panel.id === `tab-${tabId}`);
    });

    // Refresh context-specific views
    if (tabId === 'live-parking') {
      if (window.threeParking && window.threeParking.renderer) {
        window.threeParking.renderer.setSize(
          window.threeParking.container.clientWidth,
          window.threeParking.container.clientHeight
        );
      }
      if (this.state && window.parkingLotViz) {
        window.parkingLotViz.renderSchematic(this.state.slots);
      }
    } else if (tabId === 'vehicles') {
      this.renderVehiclesRegistry();
    } else if (tabId === 'entry-exit') {
      this.refreshKioskDropdowns();
    } else if (tabId === 'reservations') {
      this.renderReservationsTable();
    } else if (tabId === 'payments') {
      this.renderPaymentsTable();
    } else if (tabId === 'reports') {
      this.renderReportsMetrics();
    }
  }

  /* -------------------------------------------------------------------------
   * ACADEMIC OS LAB TAB SWITCHING
   * ------------------------------------------------------------------------- */
  switchOsLabTab(osTabId) {
    this.activeOsTab = osTabId;

    document.querySelectorAll('.os-lab-tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-ostab') === osTabId);
    });

    document.querySelectorAll('.os-lab-panel').forEach(panel => {
      if (panel.id === `ostab-${osTabId}`) {
        panel.style.display = 'block';
        panel.classList.add('active');
      } else {
        panel.style.display = 'none';
        panel.classList.remove('active');
      }
    });

    this.refreshActiveOsTab();
  }

  refreshActiveOsTab() {
    if (this.activeOsTab === 'cpu-scheduling' && window.schedulerViz) {
      window.schedulerViz.render();
      if (this.state) window.schedulerViz.updateFromLiveState(this.state);
    } else if (this.activeOsTab === 'bankers-deadlock' && window.bankersViz) {
      window.bankersViz.renderMatrices();
    } else if (this.activeOsTab === 'classical-sync' && window.classicalViz) {
      window.classicalViz.sync();
    }
  }

  /* -------------------------------------------------------------------------
   * INGRESS / EGRESS KIOSK WORKFLOWS
   * ------------------------------------------------------------------------- */
  generateRandomKioskPlate() {
    const prefixes = ['DL-01', 'UP-16', 'HR-26', 'MH-02', 'KA-05', 'RJ-14'];
    const letters = 'ABCDEFGHJKLMNPQRSTUVWXYZ';
    const vType = document.getElementById('kiosk-in-type')?.value || 'STANDARD';

    let prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
    const l1 = letters[Math.floor(Math.random() * letters.length)];
    const l2 = letters[Math.floor(Math.random() * letters.length)];
    const num = Math.floor(Math.random() * 8999 + 1000);

    if (vType === 'EV') {
      prefix += '-EV';
    } else if (vType === 'EMERGENCY') {
      prefix = 'AMB';
    }

    const plateInput = document.getElementById('kiosk-in-plate');
    if (plateInput) plateInput.value = `${prefix}-${l1}${l2}${num}`;
  }

  refreshKioskDropdowns() {
    if (!this.state) return;

    // 1. Ingress Free Bays Dropdown
    const inSlotSelect = document.getElementById('kiosk-in-slot-select');
    if (inSlotSelect) {
      const currentVal = inSlotSelect.value;
      const freeSlots = Object.values(this.state.slots).filter(s => s.status === 'FREE');
      
      inSlotSelect.innerHTML = `
        <option value="">⚡ Automatic Optimal Bay Assignment (${freeSlots.length} bays free)</option>
        ${freeSlots.map(s => `
          <option value="${s.slot_id}">${s.slot_id} — ${s.slot_type} (Bay #${s.bay_number})</option>
        `).join('')}
      `;
      if (currentVal && freeSlots.some(s => s.slot_id === currentVal)) {
        inSlotSelect.value = currentVal;
      }
    }

    // 2. Egress Occupied Spaces Dropdown
    const outSlotSelect = document.getElementById('kiosk-out-vehicle-select');
    if (outSlotSelect) {
      const currentOutVal = outSlotSelect.value;
      const occSlots = Object.values(this.state.slots).filter(s => s.status === 'OCCUPIED');

      outSlotSelect.innerHTML = `
        <option value="">-- Choose Occupied Space to Release (${occSlots.length} active) --</option>
        ${occSlots.map(s => `
          <option value="${s.slot_id}">Bay ${s.slot_id} · Plate: ${s.current_plate || 'Active Vehicle'} (${s.slot_type})</option>
        `).join('')}
      `;
      if (currentOutVal && occSlots.some(s => s.slot_id === currentOutVal)) {
        outSlotSelect.value = currentOutVal;
      }
      this.updateEgressBillPreview();
    }
  }

  async submitKioskEntry() {
    const plateInput = document.getElementById('kiosk-in-plate');
    const typeSelect = document.getElementById('kiosk-in-type');
    const slotSelect = document.getElementById('kiosk-in-slot-select');
    const durationSelect = document.getElementById('kiosk-in-duration');
    const paymentSelect = document.getElementById('kiosk-in-payment');

    const plate = plateInput?.value.trim().toUpperCase();
    if (!plate) {
      this.showToast('Validation Error', 'Please specify a vehicle registration plate number.', 'warning');
      this.playSound('alarm');
      plateInput?.focus();
      return;
    }

    const payload = {
      plate: plate,
      vehicle_type: typeSelect?.value || 'STANDARD',
      slot_id: slotSelect?.value || null,
      parking_duration_min: parseFloat(durationSelect?.value || '60'),
      payment_mode: paymentSelect?.value || 'FASTTAG',
      operator: 'Gate Attendant (Deck A)'
    };

    try {
      const res = await fetch(`${this.apiBase}/api/vehicle/entry`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (data.success) {
        this.playSound('success');
        this.showToast(
          'Vehicle Ingested & Barrier Raised',
          `Vehicle ${plate} admitted to Bay ${data.pcb.slot_id || 'Queued'}. Ticket Issued.`,
          'success'
        );
        this.logActivity('🚘', `Vehicle Ingress: ${plate}`, `Assigned to Bay ${data.pcb.slot_id} (${payload.vehicle_type}, ${payload.payment_mode})`);
        
        // Reset plate and reload state
        if (plateInput) plateInput.value = '';
        this.poll();
      } else {
        this.playSound('alarm');
        this.showToast('Ingress Denied', data.error || 'Failed to process vehicle entry.', 'error');
      }
    } catch (e) {
      this.showToast('Network Error', 'Failed to communicate with parking controller.', 'error');
    }
  }

  updateEgressBillPreview() {
    const select = document.getElementById('kiosk-out-vehicle-select');
    const slotId = select?.value;

    const elPlate = document.getElementById('bill-plate');
    const elSpace = document.getElementById('bill-space');
    const elDur = document.getElementById('bill-duration');
    const elRate = document.getElementById('bill-rate');
    const elAmt = document.getElementById('bill-amount');

    if (!slotId || !this.state || !this.state.slots[slotId]) {
      if (elPlate) elPlate.innerText = '---';
      if (elSpace) elSpace.innerText = '---';
      if (elDur) elDur.innerText = '---';
      if (elRate) elRate.innerText = '---';
      if (elAmt) elAmt.innerText = '₹0.00';
      return;
    }

    const slot = this.state.slots[slotId];
    const pcb = this.state.running_processes?.find(p => p.slot_id === slotId);

    const plate = slot.current_plate || pcb?.plate || 'Active Vehicle';
    let elapsed = 15;
    if (pcb) {
      const burst = pcb.burst_time || pcb.parking_duration_min || 15;
      const remaining = pcb.remaining_time !== undefined ? pcb.remaining_time : 0;
      elapsed = Math.max(1, burst - remaining);
    }

    let rate = this.pricingRules.base_hourly_rate || 30;
    if (slot.slot_type === 'EV_CHARGING') rate = this.pricingRules.ev_hourly_rate || 40;
    else if (slot.slot_type === 'SUV_HEAVY') rate = this.pricingRules.suv_hourly_rate || 35;
    else if (pcb?.vehicle_type === 'EMERGENCY') rate = 0;

    const billableHours = Math.max(0.25, Math.ceil((elapsed / 60) * 4) / 4);
    const amount = rate === 0 ? 0 : Math.min(this.pricingRules.daily_maximum, Math.round(billableHours * rate));

    if (elPlate) elPlate.innerText = plate;
    if (elSpace) elSpace.innerText = `${slot.slot_id} (${slot.slot_type})`;
    if (elDur) elDur.innerText = `${elapsed.toFixed(1)} mins (${billableHours.toFixed(2)} hrs billable)`;
    if (elRate) elRate.innerText = rate === 0 ? 'Exempt (Emergency)' : `₹${rate}/hr`;
    if (elAmt) elAmt.innerText = `₹${amount.toFixed(2)}`;
  }

  async submitKioskExit() {
    const select = document.getElementById('kiosk-out-vehicle-select');
    const methodSelect = document.getElementById('kiosk-out-payment-method');
    const slotId = select?.value;

    if (!slotId) {
      this.showToast('Validation Error', 'Please select an occupied bay to release.', 'warning');
      this.playSound('alarm');
      select?.focus();
      return;
    }

    await this.processVehicleExit(slotId, methodSelect?.value || 'FASTTAG');
  }

  async processVehicleExit(slotId, paymentMethod = 'FASTTAG') {
    try {
      const res = await fetch(`${this.apiBase}/api/vehicle/exit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slot_id: slotId, payment_method: paymentMethod })
      });
      const data = await res.json();

      if (data.success && data.exit_summary) {
        const summary = data.exit_summary;
        this.playSound('success');
        this.showToast(
          'Vehicle Departure Settled',
          `Space ${slotId} cleared. Payment of ₹${summary.fee.toFixed(2)} received via ${summary.payment_method}.`,
          'success'
        );

        this.logActivity('🏁', `Vehicle Exit: ${summary.plate || slotId}`, `Released ${slotId} · Paid ₹${summary.fee.toFixed(2)} (${summary.payment_method})`);

        // Show Printable Itemized Receipt Modal
        this.displayReceiptModal(summary);

        this.poll();
      } else {
        this.playSound('alarm');
        this.showToast('Departure Error', data.error || 'Failed to process vehicle exit.', 'error');
      }
    } catch (e) {
      this.showToast('Network Error', 'Failed to communicate with exit gate terminal.', 'error');
    }
  }

  displayReceiptModal(summary) {
    const modal = document.getElementById('receipt-modal');
    if (!modal) return;

    document.getElementById('rcp-no').innerText = summary.receipt_number || `RCP-${Date.now().toString().slice(-6)}`;
    document.getElementById('rcp-txn').innerText = summary.transaction_id || `TXN-${Math.floor(Math.random()*9000+1000)}`;
    document.getElementById('rcp-plate').innerText = summary.plate || '---';
    document.getElementById('rcp-space').innerText = summary.slot_id || '---';
    document.getElementById('rcp-duration').innerText = `${(summary.duration_minutes || 0).toFixed(1)} mins`;
    document.getElementById('rcp-channel').innerText = summary.payment_method || 'FASTTAG';
    document.getElementById('rcp-amount').innerText = `₹${(summary.fee || 0).toFixed(2)}`;

    modal.classList.add('active');
  }

  /* -------------------------------------------------------------------------
   * ADVANCE RESERVATIONS WORKFLOW
   * ------------------------------------------------------------------------- */
  openReservationModal() {
    const modal = document.getElementById('new-reservation-modal');
    const slotSelect = document.getElementById('res-slot-id');
    if (!modal) return;

    if (slotSelect && this.state) {
      const freeSlots = Object.values(this.state.slots).filter(s => s.status === 'FREE');
      slotSelect.innerHTML = freeSlots.map(s => `
        <option value="${s.slot_id}">${s.slot_id} — ${s.slot_type} (Bay #${s.bay_number})</option>
      `).join('');
    }

    modal.classList.add('active');
  }

  async submitNewReservation() {
    const name = document.getElementById('res-cust-name')?.value.trim();
    const phone = document.getElementById('res-cust-phone')?.value.trim();
    const plate = document.getElementById('res-plate')?.value.trim().toUpperCase();
    const vtype = document.getElementById('res-vtype')?.value || 'STANDARD';
    const slotId = document.getElementById('res-slot-id')?.value;
    const timeStr = document.getElementById('res-time-str')?.value.trim() || 'Today 16:00';
    const duration = parseFloat(document.getElementById('res-duration')?.value || '2.0');
    const notes = document.getElementById('res-notes')?.value.trim() || '';

    if (!name || !plate || !slotId) {
      this.showToast('Validation Error', 'Customer Name, Plate Number, and Space are mandatory.', 'warning');
      this.playSound('alarm');
      return;
    }

    try {
      const res = await fetch(`${this.apiBase}/api/reservations/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_name: name,
          customer_phone: phone,
          plate: plate,
          vehicle_type: vtype,
          slot_id: slotId,
          start_time_str: timeStr,
          duration_hours: duration,
          notes: notes
        })
      });

      const data = await res.json();
      if (data.success) {
        this.playSound('success');
        this.showToast('Reservation Held', `Space ${slotId} is held for ${name} (${plate}).`, 'success');
        this.logActivity('📅', `Reservation Created: ${name}`, `Space ${slotId} held for ${plate} · Arrival: ${timeStr}`);
        document.getElementById('new-reservation-modal')?.classList.remove('active');
        this.poll();
      } else {
        this.playSound('alarm');
        this.showToast('Reservation Error', data.error || 'Failed to create reservation.', 'error');
      }
    } catch (e) {
      this.showToast('Network Error', 'Failed to communicate with reservation server.', 'error');
    }
  }

  async cancelReservation(resId) {
    if (!confirm(`Cancel advance booking ${resId}?`)) return;
    try {
      const res = await fetch(`${this.apiBase}/api/reservations/cancel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reservation_id: resId })
      });
      const data = await res.json();
      if (data.success) {
        this.showToast('Reservation Cancelled', `Booking ${resId} released successfully.`, 'info');
        this.logActivity('🗑️', `Reservation Cancelled: ${resId}`, 'Space returned to available pool.');
        this.poll();
      }
    } catch (e) {
      this.showToast('Error', 'Failed to cancel reservation.', 'error');
    }
  }

  async checkinReservation(resId) {
    try {
      const res = await fetch(`${this.apiBase}/api/reservations/checkin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reservation_id: resId, payment_mode: 'FASTTAG' })
      });
      const data = await res.json();
      if (data.success) {
        this.playSound('success');
        this.showToast('Customer Admitted', `Reservation ${resId} checked in. Bay ${data.pcb?.slot_id} occupied.`, 'success');
        this.logActivity('🟢', `Reservation Check-In: ${resId}`, `Vehicle ${data.pcb?.plate} parked in ${data.pcb?.slot_id}.`);
        this.poll();
      } else {
        this.playSound('alarm');
        this.showToast('Check-In Error', data.error || 'Unable to check in reservation.', 'error');
      }
    } catch (e) {
      this.showToast('Error', 'Failed to process reservation check-in.', 'error');
    }
  }

  renderReservationsTable() {
    const tbody = document.getElementById('tbody-reservations');
    if (!tbody || !this.state) return;

    const list = this.state.reservations || [];
    if (list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; color: var(--text-dim); padding: 24px;">No advance reservations currently booked.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(r => {
      let badgeStyle = 'background: rgba(245, 158, 11, 0.15); color: var(--color-amber);';
      if (r.status === 'FULFILLED') badgeStyle = 'background: rgba(16, 231, 97, 0.15); color: var(--color-lime);';
      if (r.status === 'CANCELLED') badgeStyle = 'background: rgba(244, 63, 94, 0.15); color: var(--color-rose);';

      const canAct = r.status === 'CONFIRMED';

      return `
        <tr>
          <td><strong style="color: #fff; font-family: var(--font-mono);">${r.reservation_id}</strong></td>
          <td>${r.customer_name}</td>
          <td style="color: var(--text-muted); font-size: 0.72rem;">${r.customer_phone}</td>
          <td><span style="font-family: var(--font-mono); color: var(--color-cyan); font-weight: 700;">${r.plate}</span></td>
          <td>${r.vehicle_type}</td>
          <td><strong style="color: #fff;">${r.slot_id}</strong></td>
          <td style="font-size: 0.72rem; color: var(--text-muted);">${r.start_time_str}</td>
          <td><span style="padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; ${badgeStyle}">${r.status}</span></td>
          <td>
            ${canAct ? `
              <div style="display: flex; gap: 6px;">
                <button class="btn btn-primary" style="padding: 3px 8px; font-size: 0.68rem;" onclick="window.app.checkinReservation('${r.reservation_id}')">Admit</button>
                <button class="btn btn-outline" style="padding: 3px 8px; font-size: 0.68rem; color: var(--color-rose);" onclick="window.app.cancelReservation('${r.reservation_id}')">Cancel</button>
              </div>
            ` : `<span style="font-size: 0.68rem; color: var(--text-dim);">No Actions</span>`}
          </td>
        </tr>
      `;
    }).join('');
  }

  /* -------------------------------------------------------------------------
   * VEHICLES REGISTRY & SESSIONS TABLE
   * ------------------------------------------------------------------------- */
  renderVehiclesRegistry() {
    if (!this.state) return;

    // Filter active running vehicles
    const activeVehicles = [];
    Object.values(this.state.slots).forEach(s => {
      if (s.status === 'OCCUPIED') {
        const pcb = this.state.running_processes?.find(p => p.slot_id === s.slot_id);
        const burst = pcb?.burst_time || pcb?.parking_duration_min || 15;
        const remaining = pcb?.remaining_time !== undefined ? pcb.remaining_time : 0;
        const elapsed = Math.max(1, burst - remaining);
        
        let rate = this.pricingRules.base_hourly_rate || 30;
        if (s.slot_type === 'EV_CHARGING') rate = this.pricingRules.ev_hourly_rate || 40;
        else if (s.slot_type === 'SUV_HEAVY') rate = this.pricingRules.suv_hourly_rate || 35;
        else if (pcb?.vehicle_type === 'EMERGENCY') rate = 0;

        const fee = rate === 0 ? 0 : Math.max(rate, Math.round((elapsed / 60) * rate));

        activeVehicles.push({
          plate: s.current_plate || pcb?.plate || 'Active Vehicle',
          category: s.slot_type,
          slot_id: s.slot_id,
          entry_time: pcb?.arrival_time ? `${pcb.arrival_time.toFixed(1)}m mark` : 'Recent Ingress',
          elapsed_min: elapsed,
          fee: fee,
          payment_mode: pcb?.payment_mode || 'FASTTAG'
        });
      }
    });

    const activeCountEl = document.getElementById('vehicles-active-count');
    if (activeCountEl) activeCountEl.innerText = activeVehicles.length;

    // Filter by search query
    const filteredActive = activeVehicles.filter(v => 
      !this.vehicleSearchQuery || 
      v.plate.toLowerCase().includes(this.vehicleSearchQuery) || 
      v.slot_id.toLowerCase().includes(this.vehicleSearchQuery)
    );

    const tbodyActive = document.getElementById('tbody-active-vehicles');
    if (tbodyActive) {
      if (filteredActive.length === 0) {
        tbodyActive.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-dim); padding: 24px;">No active vehicles parked matching filter.</td></tr>`;
      } else {
        tbodyActive.innerHTML = filteredActive.map(v => `
          <tr>
            <td><strong style="color: var(--color-cyan); font-family: var(--font-mono); font-size: 0.85rem;">${v.plate}</strong></td>
            <td><span style="font-size: 0.72rem; color: var(--text-muted);">${v.category}</span></td>
            <td><strong style="color: #fff; background: rgba(255,255,255,0.06); padding: 2px 6px; border-radius: 4px;">${v.slot_id}</strong></td>
            <td style="font-size: 0.72rem; color: var(--text-dim);">${v.entry_time}</td>
            <td style="font-family: var(--font-mono); color: #fff;">${v.elapsed_min.toFixed(1)} mins</td>
            <td style="color: var(--color-lime); font-weight: 700;">₹${v.fee.toFixed(2)}</td>
            <td><span style="font-size: 0.7rem; color: var(--text-dim);">${v.payment_mode}</span></td>
            <td>
              <button class="btn btn-rose" style="padding: 3px 8px; font-size: 0.68rem;" onclick="window.app.processVehicleExit('${v.slot_id}', '${v.payment_mode}')">
                Exit &amp; Settle
              </button>
            </td>
          </tr>
        `).join('');
      }
    }

    // History Sessions from terminated list and payments
    const historyList = (this.state.terminated_processes || []).map((p, idx) => ({
      session_id: `SES-${1000 + idx}`,
      plate: p.plate,
      category: p.vehicle_type,
      slot_id: p.slot_id || 'Deck A',
      arrival: `${(p.arrival_time || 0).toFixed(1)}m`,
      departure: `${(p.completion_time || p.arrival_time + 15).toFixed(1)}m`,
      duration: `${(p.turnaround_time || 15).toFixed(1)} min`,
      fee: p.vehicle_type === 'EMERGENCY' ? 0 : 35.0,
      status: 'COMPLETED & SETTLED'
    }));

    const historyCountEl = document.getElementById('vehicles-history-count');
    if (historyCountEl) historyCountEl.innerText = historyList.length;

    const filteredHistory = historyList.filter(h => 
      !this.vehicleSearchQuery || 
      h.plate.toLowerCase().includes(this.vehicleSearchQuery)
    );

    const tbodyHistory = document.getElementById('tbody-history-vehicles');
    if (tbodyHistory) {
      if (filteredHistory.length === 0) {
        tbodyHistory.innerHTML = `<tr><td colspan="9" style="text-align: center; color: var(--text-dim); padding: 24px;">No session history archived yet today.</td></tr>`;
      } else {
        tbodyHistory.innerHTML = filteredHistory.map(h => `
          <tr>
            <td style="font-family: var(--font-mono); font-size: 0.72rem; color: var(--text-dim);">${h.session_id}</td>
            <td><strong style="color: #fff; font-family: var(--font-mono);">${h.plate}</strong></td>
            <td>${h.category}</td>
            <td><strong>${h.slot_id}</strong></td>
            <td style="font-size: 0.72rem; color: var(--text-muted);">${h.arrival}</td>
            <td style="font-size: 0.72rem; color: var(--text-muted);">${h.departure}</td>
            <td style="font-family: var(--font-mono);">${h.duration}</td>
            <td style="color: var(--color-lime); font-weight: 700;">₹${h.fee.toFixed(2)}</td>
            <td><span style="font-size: 0.68rem; color: var(--color-lime); font-weight: 700;">${h.status}</span></td>
          </tr>
        `).join('');
      }
    }
  }

  /* -------------------------------------------------------------------------
   * TARIFF PRICING & PAYMENT TRANSACTIONS
   * ------------------------------------------------------------------------- */
  async saveTariffPricing() {
    const base = parseFloat(document.getElementById('price-base-rate')?.value || '30');
    const ev = parseFloat(document.getElementById('price-ev-rate')?.value || '40');
    const suv = parseFloat(document.getElementById('price-suv-rate')?.value || '35');
    const grace = parseFloat(document.getElementById('price-grace-min')?.value || '15');
    const dailyMax = parseFloat(document.getElementById('price-daily-max')?.value || '350');

    try {
      const res = await fetch(`${this.apiBase}/api/pricing/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          base_hourly_rate: base,
          ev_hourly_rate: ev,
          suv_hourly_rate: suv,
          grace_period_min: grace,
          daily_maximum: dailyMax
        })
      });
      const data = await res.json();
      if (data.success) {
        this.pricingRules = data.pricing;
        this.playSound('success');
        this.showToast('Tariff Updated', 'Facility pricing rules saved successfully.', 'success');
        this.logActivity('⚙️', 'Tariff Configuration Saved', `Base: ₹${base}/hr, EV: ₹${ev}/hr, Grace: ${grace} min, Daily Max: ₹${dailyMax}`);
      }
    } catch (e) {
      this.showToast('Error', 'Failed to update pricing rules.', 'error');
    }
  }

  renderPaymentsTable() {
    const tbody = document.getElementById('tbody-payments');
    if (!tbody || !this.state) return;

    const list = this.state.payments || [];
    if (list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-dim); padding: 24px;">No settled payment transactions recorded yet today.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(p => `
      <tr>
        <td style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-dim);">${p.payment_id}</td>
        <td><strong style="color: #fff; font-family: var(--font-mono);">${p.receipt_number}</strong></td>
        <td><strong style="color: var(--color-cyan); font-family: var(--font-mono);">${p.plate}</strong></td>
        <td style="color: var(--color-lime); font-weight: 800; font-size: 0.9rem;">₹${p.amount.toFixed(2)}</td>
        <td><span style="font-size: 0.72rem; color: var(--text-pure);">${p.method}</span></td>
        <td style="font-size: 0.72rem; color: var(--text-muted);">${p.timestamp_str}</td>
        <td><span style="padding: 2px 6px; border-radius: 4px; font-size: 0.68rem; font-weight: 700; background: rgba(16, 231, 97, 0.15); color: var(--color-lime);">${p.status}</span></td>
      </tr>
    `).join('');
  }

  /* -------------------------------------------------------------------------
   * REPORTS, ANALYTICS & CSV EXPORT
   * ------------------------------------------------------------------------- */
  renderReportsMetrics() {
    if (!this.state) return;

    const completed = this.state.terminated_processes || [];
    let under30 = 0, mid30to60 = 0, over60 = 0;

    completed.forEach(p => {
      const dur = p.turnaround_time || 20;
      if (dur < 30) under30++;
      else if (dur <= 60) mid30to60++;
      else over60++;
    });

    const total = Math.max(1, completed.length);
    document.getElementById('rep-dur-under30').innerText = `${under30} sessions`;
    document.getElementById('rep-dur-30to60').innerText = `${mid30to60} sessions`;
    document.getElementById('rep-dur-over60').innerText = `${over60} sessions`;

    document.getElementById('rep-bar-under30').style.width = `${Math.round((under30 / total) * 100)}%`;
    document.getElementById('rep-bar-30to60').style.width = `${Math.round((mid30to60 / total) * 100)}%`;
    document.getElementById('rep-bar-over60').style.width = `${Math.round((over60 / total) * 100)}%`;

    // Payment channels breakdown
    const container = document.getElementById('rep-payment-channels');
    if (container) {
      const payments = this.state.payments || [];
      const channels = { FASTTAG: 0, UPI: 0, CARD: 0, CASH: 0 };
      payments.forEach(p => {
        const m = p.method || 'FASTTAG';
        if (channels[m] !== undefined) channels[m] += p.amount;
        else channels.FASTTAG += p.amount;
      });

      const totalRev = Math.max(1, Object.values(channels).reduce((a, b) => a + b, 0));

      container.innerHTML = Object.entries(channels).map(([chan, amt]) => {
        const pct = Math.round((amt / totalRev) * 100);
        return `
          <div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
              <span>${chan}</span>
              <strong style="color: #fff;">₹${amt.toFixed(2)} (${pct}%)</strong>
            </div>
            <div class="kpi-progress-track">
              <div class="kpi-progress-bar" style="width: ${pct}%; background: var(--color-cyan);"></div>
            </div>
          </div>
        `;
      }).join('');
    }
  }

  exportOperationalAuditCsv() {
    if (!this.state) return;
    this.playSound('click');

    const headers = ['Record_Type', 'Reference_ID', 'Plate', 'Space_ID', 'Duration_Min', 'Amount_INR', 'Payment_Method', 'Timestamp'];
    const rows = [headers];

    // Summary row
    rows.push([
      'DAILY_SUMMARY',
      `FAC-01`,
      `ALL_VEHICLES`,
      `TOTAL_BAYS_16`,
      `N/A`,
      (this.state.stats?.daily_revenue || 0).toFixed(2),
      `TOTAL_TXNS_${this.state.stats?.total_payments_count || 0}`,
      new Date().toISOString()
    ]);

    // Payment transactions
    (this.state.payments || []).forEach(p => {
      rows.push([
        'PAYMENT_TXN',
        p.payment_id,
        p.plate,
        p.slot_id,
        p.duration_minutes.toFixed(1),
        p.amount.toFixed(2),
        p.method,
        p.timestamp_str
      ]);
    });

    // Reservations
    (this.state.reservations || []).forEach(r => {
      rows.push([
        'RESERVATION',
        r.reservation_id,
        r.plate,
        r.slot_id,
        (r.duration_hours * 60).toFixed(1),
        'HOLD',
        r.status,
        r.start_time_str
      ]);
    });

    const csvContent = 'data:text/csv;charset=utf-8,' + rows.map(e => e.join(',')).join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `nexus_park_operational_audit_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    this.showToast('Audit Exported', 'Operational CSV audit report downloaded.', 'success');
  }

  /* -------------------------------------------------------------------------
   * TRAFFIC SURGE SIMULATION (Multi-tier batch ingestion)
   * ------------------------------------------------------------------------- */
  async triggerTrafficSurge() {
    this.playSound('lock');
    this.showToast('Traffic Surge', 'Ingesting 4 concurrent vehicles with diverse categories...', 'info');

    const burstList = [
      { plate: 'AMB-911', vehicle_type: 'EMERGENCY', parking_duration_min: 15, payment_mode: 'CASH' },
      { plate: 'UP-16-EV8821', vehicle_type: 'EV', parking_duration_min: 45, payment_mode: 'FASTTAG' },
      { plate: 'HR-26-SUV400', vehicle_type: 'SUV', parking_duration_min: 60, payment_mode: 'UPI' },
      { plate: 'DL-01-SEDAN12', vehicle_type: 'STANDARD', parking_duration_min: 30, payment_mode: 'CARD' }
    ];

    for (const v of burstList) {
      try {
        await fetch(`${this.apiBase}/api/vehicle/entry`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(v)
        });
      } catch (e) {}
    }

    this.logActivity('⚡', 'Traffic Surge Ingested', '4 concurrent vehicles arrived at Terminal Gate.');
    setTimeout(() => this.poll(), 400);
  }

  /* -------------------------------------------------------------------------
   * SYSTEM POLLING & STATE SYNCHRONIZATION
   * ------------------------------------------------------------------------- */
  startPolling() {
    this.poll();
    this.pollInterval = setInterval(() => this.poll(), 1000);
  }

  async poll() {
    try {
      const res = await fetch(`${this.apiBase}/api/status`);
      if (res.ok) {
        const state = await res.json();
        this.renderState(state);
      }
    } catch (e) {
      // Backend not yet ready or polling interrupted
    }
  }

  renderState(state) {
    if (!state) return;
    this.state = state;

    if (state.pricing_rules) {
      this.pricingRules = state.pricing_rules;
    }

    // 1. Dominant Commercial Overview KPIs
    const total = state.stats.total_slots || 16;
    const occupied = state.stats.occupied_slots || 0;
    const reserved = state.stats.reserved_slots || 0;
    const free = state.stats.free_slots || (total - occupied - reserved);
    const occPct = ((occupied + reserved) / total) * 100;
    const availPct = (free / total) * 100;

    const elAvail = document.getElementById('ov-avail-spaces');
    const elTotal = document.getElementById('ov-total-cap');
    const elAvailBar = document.getElementById('ov-avail-bar');
    const elOccPct = document.getElementById('ov-occupancy-pct');
    const elOccCount = document.getElementById('ov-occupied-count');
    const elOccBar = document.getElementById('ov-occ-bar');
    const elEntries = document.getElementById('ov-entries-today');
    const elExits = document.getElementById('ov-exits-today');
    const elRev = document.getElementById('ov-revenue-today');
    const elTxns = document.getElementById('ov-txns-count');

    if (elAvail) elAvail.innerText = free;
    if (elTotal) elTotal.innerText = total;
    if (elAvailBar) elAvailBar.style.width = `${availPct}%`;

    if (elOccPct) elOccPct.innerText = `${occPct.toFixed(1)}%`;
    if (elOccCount) elOccCount.innerText = occupied;
    if (elOccBar) elOccBar.style.width = `${occPct}%`;

    if (elEntries) elEntries.innerText = state.stats.daily_entries || 0;
    if (elExits) elExits.innerText = state.stats.daily_exits || 0;
    if (elRev) elRev.innerText = `₹${(state.stats.daily_revenue || 0).toFixed(2)}`;
    if (elTxns) elTxns.innerText = state.stats.total_payments_count || 0;

    // 2. Delegate to Visualizers
    if (window.threeParking) {
      window.threeParking.updateSlots(state.slots);
    }
    if (window.parkingLotViz) {
      window.parkingLotViz.render(state);
    }

    // 3. Delegate to Active Commercial View
    if (this.activeTab === 'vehicles') {
      this.renderVehiclesRegistry();
    } else if (this.activeTab === 'entry-exit') {
      this.refreshKioskDropdowns();
    } else if (this.activeTab === 'reservations') {
      this.renderReservationsTable();
    } else if (this.activeTab === 'payments') {
      this.renderPaymentsTable();
    } else if (this.activeTab === 'reports') {
      this.renderReportsMetrics();
    }

    // 4. Delegate to Academic OS Lab if Open
    const osLabModal = document.getElementById('os-lab-modal');
    if (osLabModal && osLabModal.classList.contains('active')) {
      if (this.activeOsTab === 'cpu-scheduling' && window.schedulerViz) {
        window.schedulerViz.updateFromLiveState(state);
      }
    }
  }
}

// Instantiate upon DOM load
window.addEventListener('DOMContentLoaded', () => {
  window.app = new SmartParkingApp();
});
