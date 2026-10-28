/**
 * NEXUS-PARK // Live Space Visualizer & Commercial Operations Drawer
 * Handles 2D Schematic Plan, 3D Map Interactions, & Maintenance Toggles
 */

class ParkingLotVisualizer {
  constructor() {
    this.selectedSlotId = null;
    this.activeFilter = 'ALL';
    this.bindEvents();
  }

  bindEvents() {
    // Space Detail Modal
    const modal = document.getElementById('space-detail-modal');
    const closeBtn = document.getElementById('close-space-modal');
    const closeBtn2 = document.getElementById('btn-space-close');
    const toggleMaintBtn = document.getElementById('btn-space-toggle-maint');
    const releaseBtn = document.getElementById('btn-space-release-action');

    const closeModal = () => {
      if (modal) modal.classList.remove('active');
      this.selectedSlotId = null;
      if (window.threeParking) {
        window.threeParking.selectSlot(null);
      }
    };

    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (closeBtn2) closeBtn2.addEventListener('click', closeModal);
    if (modal) {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
      });
    }

    if (toggleMaintBtn) {
      toggleMaintBtn.addEventListener('click', () => {
        if (this.selectedSlotId) {
          this.toggleSlotMaintenance(this.selectedSlotId);
        }
      });
    }

    if (releaseBtn) {
      releaseBtn.addEventListener('click', () => {
        if (this.selectedSlotId) {
          window.app.processVehicleExit(this.selectedSlotId);
          closeModal();
        }
      });
    }

    // Filter Pills
    document.querySelectorAll('#space-filter-pills .filter-pill').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#space-filter-pills .filter-pill').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        this.activeFilter = btn.getAttribute('data-filter') || 'ALL';
        if (window.threeParking) {
          window.threeParking.setFilter(this.activeFilter);
        }
        if (window.app && window.app.state) {
          this.renderSchematic(window.app.state.slots);
        }
        if (window.app) window.app.playSound('click');
      });
    });

    // Map Search Input
    const mapSearch = document.getElementById('map-search-input');
    if (mapSearch) {
      mapSearch.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        if (window.threeParking) {
          window.threeParking.setSearch(query);
        }
        if (window.app && window.app.state) {
          this.renderSchematic(window.app.state.slots, query);
        }
      });
    }
  }

  render(state) {
    if (!state) return;

    // Update filter counts in pills
    const slots = Object.values(state.slots || {});
    const availCount = slots.filter(s => s.status === 'FREE').length;
    const occCount = slots.filter(s => s.status === 'OCCUPIED').length;
    const resCount = slots.filter(s => s.status === 'RESERVED').length;
    const maintCount = slots.filter(s => s.status === 'OUT_OF_SERVICE').length;

    const elAvail = document.getElementById('pill-avail-count');
    const elOcc = document.getElementById('pill-occ-count');
    const elRes = document.getElementById('pill-res-count');
    const elMaint = document.getElementById('pill-maint-count');

    if (elAvail) elAvail.innerText = availCount;
    if (elOcc) elOcc.innerText = occCount;
    if (elRes) elRes.innerText = resCount;
    if (elMaint) elMaint.innerText = maintCount;

    // Render 2D Schematic
    this.renderSchematic(state.slots);
  }

  renderSchematic(slots, searchQuery = '') {
    if (!slots) return;
    const query = searchQuery || (document.getElementById('map-search-input')?.value || '').toLowerCase().trim();

    const rowA = document.getElementById('schematic-row-a');
    const rowB = document.getElementById('schematic-row-b');
    const rowC = document.getElementById('schematic-row-c');
    const rowD = document.getElementById('schematic-row-d');

    if (!rowA || !rowB || !rowC || !rowD) return;

    let htmlA = '', htmlB = '', htmlC = '', htmlD = '';

    Object.values(slots).sort((a, b) => a.bay_number - b.bay_number).forEach(slot => {
      // 1. Filter Check
      if (this.activeFilter === 'AVAILABLE' && slot.status !== 'FREE') return;
      if (this.activeFilter === 'OCCUPIED' && slot.status !== 'OCCUPIED') return;
      if (this.activeFilter === 'RESERVED' && slot.status !== 'RESERVED') return;
      if (this.activeFilter === 'MAINTENANCE' && slot.status !== 'OUT_OF_SERVICE') return;

      // 2. Search Check
      if (query) {
        const matchesPlate = (slot.current_plate || '').toLowerCase().includes(query);
        const matchesSlot = slot.slot_id.toLowerCase().includes(query);
        if (!matchesPlate && !matchesSlot) return;
      }

      const cardHtml = this.generateSchematicCard(slot);
      if (slot.bay_number <= 8) htmlA += cardHtml;
      else if (slot.bay_number <= 12) htmlB += cardHtml;
      else if (slot.bay_number <= 14) htmlC += cardHtml;
      else htmlD += cardHtml;
    });

    rowA.innerHTML = htmlA || '<div style="color: var(--text-dim); font-size: 0.72rem; padding: 10px;">No matching spaces.</div>';
    rowB.innerHTML = htmlB || '<div style="color: var(--text-dim); font-size: 0.72rem; padding: 10px;">No matching spaces.</div>';
    rowC.innerHTML = htmlC || '<div style="color: var(--text-dim); font-size: 0.72rem; padding: 10px;">No matching spaces.</div>';
    rowD.innerHTML = htmlD || '<div style="color: var(--text-dim); font-size: 0.72rem; padding: 10px;">No matching spaces.</div>';
  }

  generateSchematicCard(slot) {
    const isOcc = slot.status === 'OCCUPIED';
    const isRes = slot.status === 'RESERVED';
    const isMaint = slot.status === 'OUT_OF_SERVICE';

    let statusClass = 'status-free';
    let statusLabel = 'AVAILABLE';
    let statusColor = 'var(--color-lime)';

    if (isOcc) {
      statusClass = 'status-occupied';
      statusLabel = 'OCCUPIED';
      statusColor = 'var(--color-cyan)';
    } else if (isRes) {
      statusClass = 'status-reserved';
      statusLabel = 'RESERVED';
      statusColor = 'var(--color-amber)';
    } else if (isMaint) {
      statusClass = 'status-maint';
      statusLabel = 'MAINTENANCE';
      statusColor = 'var(--color-rose)';
    }

    let typeTag = 'Compact';
    if (slot.slot_type === 'EV_CHARGING') typeTag = '⚡ EV Bay';
    else if (slot.slot_type === 'SUV_HEAVY') typeTag = '🚙 Heavy SUV';
    else if (slot.slot_type === 'VALET') typeTag = '⭐ Valet / VIP';

    let bodyHtml = '';
    if (isOcc) {
      bodyHtml = `
        <div style="font-family: var(--font-mono); font-size: 0.8rem; font-weight: 700; color: var(--color-cyan); margin: 6px 0;">
          ${slot.current_plate}
        </div>
        <div style="font-size: 0.68rem; color: var(--text-dim);">PID: ${slot.current_pid}</div>
      `;
    } else if (isRes) {
      bodyHtml = `
        <div style="font-size: 1.2rem; opacity: 0.4;">📅</div>
        <div style="font-size: 0.72rem; font-weight: 700; color: var(--color-amber);">BOOKED</div>
      `;
    } else if (isMaint) {
      bodyHtml = `
        <div style="font-size: 1.2rem; opacity: 0.4;">🚫</div>
        <div style="font-size: 0.7rem; font-weight: 700; color: var(--color-rose);">OFFLINE</div>
      `;
    } else {
      bodyHtml = `
        <div style="font-size: 1.2rem; opacity: 0.3;">🅿️</div>
        <div style="font-size: 0.72rem; font-weight: 700; color: var(--color-lime);">AVAILABLE</div>
      `;
    }

    return `
      <div class="kpi-card" style="padding: 12px; min-height: 125px; cursor: pointer; --card-accent: ${statusColor};" onclick="window.parkingLotViz.inspectSlot('${slot.slot_id}')">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <strong style="font-family: var(--font-mono); font-size: 0.88rem; color: #fff;">${slot.slot_id}</strong>
          <span style="font-size: 0.62rem; color: var(--text-dim);">${typeTag}</span>
        </div>
        <div style="text-align: center; margin: 8px 0;">
          ${bodyHtml}
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.65rem; color: var(--text-dim); border-top: 1px solid rgba(255,255,255,0.05); padding-top: 4px;">
          <span>Bay #${slot.bay_number}</span>
          <span>Served: ${slot.total_vehicles_served}</span>
        </div>
      </div>
    `;
  }

  inspectSlot(slotId) {
    this.selectedSlotId = slotId;
    if (window.threeParking) {
      window.threeParking.selectSlot(slotId);
    }

    const state = window.app?.state;
    if (!state || !state.slots[slotId]) return;

    const slot = state.slots[slotId];
    const modal = document.getElementById('space-detail-modal');
    if (!modal) return;

    document.getElementById('space-modal-title').innerText = `🅿️ Space Details: ${slot.slot_id}`;
    document.getElementById('space-modal-subtitle').innerText = `Bay Category: ${slot.slot_type} · Bay #${slot.bay_number}`;

    const statusBadge = document.getElementById('space-modal-status-badge');
    const plateEl = document.getElementById('space-modal-plate');
    const bayNoEl = document.getElementById('space-modal-bayno');
    const servedEl = document.getElementById('space-modal-served');
    const timeParkedEl = document.getElementById('space-modal-parked-time');
    const feeEl = document.getElementById('space-modal-accrued-fee');
    const releaseBtn = document.getElementById('btn-space-release-action');
    const maintBtn = document.getElementById('btn-space-toggle-maint');

    bayNoEl.innerText = `Hardware Bay #${slot.bay_number}`;
    servedEl.innerText = `${slot.total_vehicles_served} vehicles`;

    let statusColor = 'var(--color-lime)';
    let statusLabel = 'AVAILABLE';
    plateEl.innerText = '[ None ]';
    timeParkedEl.innerText = '---';
    feeEl.innerText = '₹0.00';
    releaseBtn.style.display = 'none';

    if (slot.status === 'OCCUPIED') {
      statusColor = 'var(--color-cyan)';
      statusLabel = 'OCCUPIED';
      plateEl.innerText = slot.current_plate || 'PARKED';
      releaseBtn.style.display = 'inline-flex';

      // Find running session for duration & fee calculation
      const pcb = state.running_processes?.find(p => p.slot_id === slot.slot_id);
      if (pcb) {
        const remaining = pcb.remaining_time !== undefined ? pcb.remaining_time : 0;
        const burst = pcb.burst_time || pcb.parking_duration_min || 15;
        const elapsed = Math.max(0, burst - remaining);
        timeParkedEl.innerText = `${elapsed.toFixed(1)} min elapsed (Est. ${pcb.parking_duration_min} min)`;

        // Estimate current fee
        let rate = 30;
        if (slot.slot_type === 'EV_CHARGING') rate = 40;
        else if (slot.slot_type === 'SUV_HEAVY') rate = 35;
        else if (slot.slot_type === 'VALET' && pcb.vehicle_type === 'EMERGENCY') rate = 0;

        const hrs = Math.max(1, elapsed / 60);
        feeEl.innerText = rate === 0 ? 'FREE (Priority)' : `₹${(hrs * rate).toFixed(2)}`;
      }
    } else if (slot.status === 'RESERVED') {
      statusColor = 'var(--color-amber)';
      statusLabel = 'RESERVED (Booking Held)';
      if (slot.assigned_reservation_id) {
        plateEl.innerText = `Held for ${slot.assigned_reservation_id}`;
      }
    } else if (slot.status === 'OUT_OF_SERVICE') {
      statusColor = 'var(--color-rose)';
      statusLabel = `OUT OF SERVICE (${slot.maintenance_reason || 'Maintenance'})`;
    }

    statusBadge.innerText = statusLabel;
    statusBadge.style.color = statusColor;

    // Maintenance toggle button text
    if (maintBtn) {
      if (slot.status === 'OUT_OF_SERVICE') {
        maintBtn.innerText = '✅ Return to Active Service';
      } else {
        maintBtn.innerText = '⚠️ Set Out of Service (Maintenance)';
      }
    }

    modal.classList.add('active');
    if (window.app) window.app.playSound('click');
  }

  async toggleSlotMaintenance(slotId) {
    const slot = window.app?.state?.slots[slotId];
    if (!slot) return;

    const outOfService = slot.status !== 'OUT_OF_SERVICE';
    try {
      const res = await fetch(`${window.app.apiBase}/api/slot/maintenance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slot_id: slotId, out_of_service: outOfService })
      });
      const data = await res.json();
      if (data.success) {
        window.app.showToast('Maintenance Status', `Space ${slotId} is now ${outOfService ? 'OUT OF SERVICE' : 'AVAILABLE'}.`, outOfService ? 'warning' : 'success');
        document.getElementById('space-detail-modal')?.classList.remove('active');
        window.app.poll();
      } else {
        window.app.showToast('Action Denied', data.error || 'Failed to toggle maintenance status.', 'error');
      }
    } catch (e) {
      console.warn('Maintenance error', e);
    }
  }
}

window.ParkingLotVisualizer = ParkingLotVisualizer;
