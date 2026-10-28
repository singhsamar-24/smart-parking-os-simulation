/**
 * NEXUS-PARK // Concurrency & Synchronization Lab
 * Unit 3: Race Conditions, Peterson's Algorithm, TSL, & Counting Semaphore
 */

class ConcurrencyVisualizer {
  constructor() {
    this.raceMode = 'unsync';
    this.petersonStep = 0;
    this.petersonData = null;
    this.bindEvents();
  }

  bindEvents() {
    // Mode toggles
    const btnUnsync = document.getElementById('btn-race-unsync');
    const btnSync = document.getElementById('btn-race-sync');
    if (btnUnsync && btnSync) {
      btnUnsync.addEventListener('click', () => {
        this.raceMode = 'unsync';
        btnUnsync.classList.add('active');
        btnSync.classList.remove('active');
        if (window.app) window.app.playSound('click');
      });
      btnSync.addEventListener('click', () => {
        this.raceMode = 'sync';
        btnSync.classList.add('active');
        btnUnsync.classList.remove('active');
        if (window.app) window.app.playSound('click');
      });
    }

    // Run Race Test
    const runRaceBtn = document.getElementById('btn-run-race-sim');
    if (runRaceBtn) {
      runRaceBtn.addEventListener('click', () => {
        this.executeRaceSimulation();
      });
    }

    // Peterson Step button
    const petersonStepBtn = document.getElementById('btn-peterson-step');
    if (petersonStepBtn) {
      petersonStepBtn.addEventListener('click', () => {
        this.stepPetersonsAlgorithm();
      });
    }

    // TSL Trace button
    const tslTraceBtn = document.getElementById('btn-tsl-trace');
    if (tslTraceBtn) {
      tslTraceBtn.addEventListener('click', () => {
        this.traceTestAndSet();
      });
    }

    // Counting Semaphore Buttons
    const semWaitBtn = document.getElementById('btn-sem-wait');
    const semSignalBtn = document.getElementById('btn-sem-signal');
    if (semWaitBtn) {
      semWaitBtn.addEventListener('click', () => {
        this.executeSemaphoreAction('WAIT');
      });
    }
    if (semSignalBtn) {
      semSignalBtn.addEventListener('click', () => {
        this.executeSemaphoreAction('SIGNAL');
      });
    }
  }

  async traceTestAndSet() {
    try {
      const res = await fetch(`${window.app.apiBase}/api/concurrency/tsl`);
      const data = await res.json();
      const tslBox = document.getElementById('tsl-trace-log');
      if (tslBox && data.steps) {
        tslBox.innerHTML = data.steps.map(s => `
          <div style="padding: 8px 12px; background: rgba(255,255,255,0.03); border-left: 3px solid var(--color-cyan); margin-bottom: 6px; border-radius: var(--radius-xs); font-size: 0.76rem; font-family: var(--font-mono);">
            <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
              <strong style="color: #fff;">Step ${s.step}: ${s.process}</strong>
              <span style="color: var(--color-amber);">${s.hardware_state}</span>
            </div>
            <div style="color: var(--color-cyan); margin-bottom: 2px;">
              <code>${s.instruction}</code>
            </div>
            <div style="color: var(--text-dim); font-size: 0.72rem;">${s.result}</div>
          </div>
        `).join('');
      }
      if (window.app) {
        window.app.playSound('click');
        window.app.showToast('Hardware TSL', 'Test-and-Set Lock atomic machine instruction executed.', 'info');
      }
    } catch (e) {
      console.warn('TSL error', e);
    }
  }

  async executeRaceSimulation() {
    const traceBox = document.getElementById('race-condition-trace-container');
    const stateBox = document.getElementById('race-final-state-box');

    if (window.app) {
      window.app.showToast('Race Commenced', `Executing ${this.raceMode.toUpperCase()} slot allocation concurrency test...`, 'info');
      window.app.playSound('click');
    }

    try {
      const res = await fetch(`${window.app.apiBase}/api/concurrency/race`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode: this.raceMode,
          slot_id: 'S05',
          vehicle_a: 'Vehicle-A (P101)',
          vehicle_b: 'Vehicle-B (P102)'
        })
      });
      const data = await res.json();

      if (traceBox && data.trace) {
        traceBox.innerHTML = data.trace.map(t => `
          <div style="padding: 8px 12px; background: rgba(255,255,255,0.02); border-left: 3px solid ${t.thread.includes('Thread A') ? 'var(--color-indigo)' : 'var(--color-amber)'}; margin-bottom: 6px; border-radius: 4px; font-size: 0.78rem; font-family: var(--font-mono);">
            <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
              <strong style="color: #fff;">Step ${t.step}: ${t.thread}</strong>
              <span style="color: var(--color-cyan);">${t.action}</span>
            </div>
            <div style="color: var(--text-muted); font-size: 0.72rem;">${t.detail}</div>
          </div>
        `).join('');
      }

      if (stateBox) {
        if (this.raceMode === 'unsync') {
          stateBox.style.borderColor = 'var(--color-rose)';
          stateBox.style.background = 'rgba(239, 68, 68, 0.1)';
          stateBox.innerHTML = `
            <div style="font-family: var(--font-mono); font-size: 1.1rem; font-weight: 800; color: var(--color-rose);">💥 RACE COLLISION!</div>
            <div style="font-size: 0.75rem; color: #fca5a5; margin-top: 4px;">Double Booked: Both Car A &amp; B allocated S05! Mutual exclusion violated.</div>
          `;
          if (window.app) {
            window.app.playSound('alarm');
            window.app.showToast('Race Condition Detected!', data.hazard, 'error');
          }
        } else {
          stateBox.style.borderColor = 'var(--color-lime)';
          stateBox.style.background = 'rgba(16, 231, 97, 0.1)';
          stateBox.innerHTML = `
            <div style="font-family: var(--font-mono); font-size: 1.1rem; font-weight: 800; color: var(--color-lime);">🔒 MUTEX PROTECTED</div>
            <div style="font-size: 0.75rem; color: #a7f3d0; margin-top: 4px;">Car A acquired Mutex. Car B redirected safely to next free bay S06.</div>
          `;
          if (window.app) {
            window.app.playSound('success');
            window.app.showToast('Critical Section Protected', 'Mutual exclusion maintained via Mutex.', 'success');
          }
        }
      }

    } catch (e) {
      console.warn('Race test error', e);
    }
  }

  async stepPetersonsAlgorithm() {
    if (!this.petersonData) {
      try {
        const res = await fetch(`${window.app.apiBase}/api/concurrency/peterson`);
        this.petersonData = await res.json();
      } catch (e) {
        return;
      }
    }

    const steps = this.petersonData.steps;
    const currentStepObj = steps[this.petersonStep % steps.length];
    this.petersonStep++;

    const f0 = document.getElementById('peterson-flag0');
    const f1 = document.getElementById('peterson-flag1');
    const turn = document.getElementById('peterson-turn');
    const log = document.getElementById('peterson-step-log');

    if (f0) {
      f0.innerText = currentStepObj.flag_0 ? 'TRUE' : 'FALSE';
      f0.style.color = currentStepObj.flag_0 ? 'var(--color-lime)' : 'var(--text-dim)';
    }

    if (f1) {
      f1.innerText = currentStepObj.flag_1 ? 'TRUE' : 'FALSE';
      f1.style.color = currentStepObj.flag_1 ? 'var(--color-amber)' : 'var(--text-dim)';
    }

    if (turn) {
      turn.innerText = currentStepObj.turn;
    }

    if (log) {
      log.innerHTML = `
        <div style="font-weight: 700; color: var(--color-cyan); margin-bottom: 4px;">
          [Step ${currentStepObj.step}] ${currentStepObj.process}: <code>${currentStepObj.code}</code>
        </div>
        <div style="color: var(--text-muted); font-size: 0.78rem;">${currentStepObj.explanation}</div>
      `;
    }

    if (window.app) window.app.playSound('click');
  }

  async executeSemaphoreAction(action) {
    try {
      const res = await fetch(`${window.app.apiBase}/api/concurrency/semaphore`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, pid: `P${Math.floor(Math.random() * 900 + 100)}` })
      });
      const data = await res.json();

      const semValEl = document.getElementById('semaphore-value-big');
      if (semValEl) {
        semValEl.innerText = data.semaphore_value;
        semValEl.style.color = data.semaphore_value <= 0 ? 'var(--color-rose)' : 'var(--color-lime)';
      }

      const queueEl = document.getElementById('semaphore-blocked-threads');
      if (queueEl) {
        if (!data.blocked_queue || data.blocked_queue.length === 0) {
          queueEl.innerText = 'None (Capacity available)';
          queueEl.style.color = 'var(--text-muted)';
        } else {
          queueEl.innerHTML = data.blocked_queue.map(p => `
            <span style="display: inline-block; background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; padding: 2px 8px; border-radius: 4px; margin-right: 4px; font-size: 0.72rem;">
              ${p} (BLOCKED)
            </span>
          `).join('');
        }
      }

      if (window.app) {
        window.app.playSound(data.semaphore_value < 0 ? 'alarm' : 'lock');
        window.app.showToast('Semaphore Action', data.message, data.semaphore_value < 0 ? 'warning' : 'success');
      }
    } catch (e) {
      console.warn('Semaphore error', e);
    }
  }
}

window.ConcurrencyVisualizer = ConcurrencyVisualizer;
