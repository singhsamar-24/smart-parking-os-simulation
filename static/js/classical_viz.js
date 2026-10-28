/**
 * NEXUS-PARK // Classical Synchronization Visualizer
 * Unit 3: Producer-Consumer, Reader-Writer, Sleeping Barber, Dining Philosophers
 */

class ClassicalVisualizer {
  constructor() {
    this.bindEvents();
  }

  bindEvents() {
    // 1. Producer-Consumer
    const produceBtn = document.getElementById('btn-pc-produce');
    const consumeBtn = document.getElementById('btn-pc-consume');
    if (produceBtn) {
      produceBtn.addEventListener('click', () => this.sendAction('producer_consumer', 'produce'));
    }
    if (consumeBtn) {
      consumeBtn.addEventListener('click', () => this.sendAction('producer_consumer', 'consume'));
    }

    // 2. Reader-Writer
    const readBtn = document.getElementById('btn-rw-read');
    const stopReadBtn = document.getElementById('btn-rw-stop-read');
    const writeBtn = document.getElementById('btn-rw-write');
    const stopWriteBtn = document.getElementById('btn-rw-stop-write');
    if (readBtn) {
      readBtn.addEventListener('click', () => this.sendAction('reader_writer', 'start_read', { reader_id: `Signboard-${Math.floor(Math.random()*90 + 10)}` }));
    }
    if (stopReadBtn) {
      stopReadBtn.addEventListener('click', () => this.sendAction('reader_writer', 'stop_read'));
    }
    if (writeBtn) {
      writeBtn.addEventListener('click', () => this.sendAction('reader_writer', 'start_write', { writer_id: 'Gate-Alloc-Writer', slot_count: Math.floor(Math.random()*10 + 5) }));
    }
    if (stopWriteBtn) {
      stopWriteBtn.addEventListener('click', () => this.sendAction('reader_writer', 'stop_write'));
    }

    // 3. Sleeping Barber
    const barberArriveBtn = document.getElementById('btn-barber-arrive');
    const barberFinishBtn = document.getElementById('btn-barber-finish');
    if (barberArriveBtn) {
      barberArriveBtn.addEventListener('click', () => this.sendAction('sleeping_barber', 'arrive'));
    }
    if (barberFinishBtn) {
      barberFinishBtn.addEventListener('click', () => this.sendAction('sleeping_barber', 'finish'));
    }

    // 4. Dining Philosophers Roundabout
    const dpDeadlockBtn = document.getElementById('btn-dp-deadlock');
    const dpResolveBtn = document.getElementById('btn-dp-resolve');
    if (dpDeadlockBtn) {
      dpDeadlockBtn.addEventListener('click', () => this.sendAction('dining_philosophers', 'deadlock'));
    }
    if (dpResolveBtn) {
      dpResolveBtn.addEventListener('click', () => this.sendAction('dining_philosophers', 'resolve'));
    }
  }

  async sync() {
    try {
      const res = await fetch(`${window.app.apiBase}/api/classical/state`);
      const data = await res.json();
      this.renderState(data);
    } catch (e) {
      console.warn('Classical sync error', e);
    }
  }

  async sendAction(subsystem, action, payload = {}) {
    if (window.app) window.app.playSound('click');
    try {
      const res = await fetch(`${window.app.apiBase}/api/classical/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subsystem, action, ...payload })
      });
      const data = await res.json();
      if (data.message && window.app) {
        window.app.showToast(subsystem.replace('_', ' ').toUpperCase(), data.message, data.success === false ? 'warning' : 'info');
      }
      if (data.deadlock && window.app) {
        window.app.playSound('alarm');
      }
      await this.sync();
    } catch (e) {
      console.warn('Classical action error', e);
    }
  }

  renderState(data) {
    if (!data) return;

    // 1. Producer Consumer Bounded Buffer
    const pc = data.producer_consumer;
    const bufferContainer = document.getElementById('pc-buffer-cells');
    const pcMsg = document.getElementById('pc-status-msg');
    if (bufferContainer && pc) {
      let cellsHtml = '';
      for (let i = 0; i < pc.capacity; i++) {
        const item = pc.queue[i];
        if (item) {
          cellsHtml += `
            <div style="flex: 1; height: 50px; background: rgba(0, 240, 255, 0.15); border: 1px solid var(--color-cyan); border-radius: var(--radius-xs); display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: var(--font-mono); font-size: 0.72rem; color: #fff;">
              <span style="font-size: 0.85rem;">🚘</span>
              <span>${item}</span>
            </div>
          `;
        } else {
          cellsHtml += `
            <div style="flex: 1; height: 50px; background: rgba(255,255,255,0.02); border: 1px dashed var(--border-subtle); border-radius: var(--radius-xs); display: flex; align-items: center; justify-content: center; font-family: var(--font-mono); font-size: 0.68rem; color: var(--text-dim);">
              [Empty]
            </div>
          `;
        }
      }
      bufferContainer.innerHTML = cellsHtml;
      if (pcMsg) {
        pcMsg.innerText = `Occupancy: ${pc.queue.length} / ${pc.capacity} | Empty Semaphore: ${pc.empty_slots} | Full Semaphore: ${pc.full_slots}`;
      }
    }

    // 2. Reader-Writer
    const rw = data.reader_writer;
    const rwDisplay = document.getElementById('rw-state-display');
    if (rwDisplay && rw) {
      rwDisplay.innerHTML = `
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
          <span>Active Readers: <strong style="color: var(--color-cyan);">${rw.readers_count}</strong> (${rw.active_readers.join(', ') || 'None'})</span>
          <span>Active Writer: <strong style="${rw.active_writer ? 'color: var(--color-rose);' : 'color: var(--color-lime);'}">${rw.active_writer || 'None'}</strong></span>
        </div>
        <div style="color: var(--text-dim); font-size: 0.72rem;">Shared Display Bay Count Value: <strong style="color: #fff;">${rw.shared_slot_count} bays</strong></div>
      `;
    }

    // 3. Sleeping Barber
    const sb = data.sleeping_barber;
    const barberDisplay = document.getElementById('barber-state-display');
    if (barberDisplay && sb) {
      let stateColor = 'var(--color-cyan)';
      if (sb.state === 'SLEEPING') stateColor = 'var(--text-dim)';
      else if (sb.state === 'SERVICING') stateColor = 'var(--color-lime)';

      barberDisplay.innerHTML = `
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
          <span>Attendant State: <strong style="color: ${stateColor};">${sb.state}</strong></span>
          <span>Currently Servicing: <strong style="color: #fff;">${sb.current_car || 'None'}</strong></span>
        </div>
        <div style="color: var(--text-dim); font-size: 0.72rem;">
          Waiting Chairs (4 Max): <span style="color: var(--color-amber);">${sb.waiting_chairs.join(', ') || '[ All Chairs Empty ]'}</span>
        </div>
      `;
    }

    // 4. Dining Philosophers
    const dp = data.dining_philosophers;
    const dpDisplay = document.getElementById('dp-state-display');
    if (dpDisplay && dp) {
      dpDisplay.innerHTML = `
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
          <span>Roundabout State: <strong style="${dp.deadlock ? 'color: var(--color-rose);' : 'color: var(--color-lime);'}">${dp.deadlock ? '🚨 CIRCULAR DEADLOCK' : '🟢 TRAFFIC FLOWING'}</strong></span>
          <span>Cars Crossing: <strong style="color: #fff;">${dp.active_crossings || 0} / 5</strong></span>
        </div>
        <div style="color: var(--text-dim); font-size: 0.72rem;">
          Sector Locks Held: <code style="color: var(--color-cyan);">${JSON.stringify(dp.sector_locks || [])}</code>
        </div>
      `;
    }
  }
}

window.ClassicalVisualizer = ClassicalVisualizer;
