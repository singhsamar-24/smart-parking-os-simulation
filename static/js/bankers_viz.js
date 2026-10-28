/**
 * NEXUS-PARK // Banker's Algorithm & Deadlock Studio
 * Unit 3: Concurrency and Deadlock Management
 * Implements Banker's Safety Algorithm, Resource Request, Coffman Conditions, and RAG Cycle Detection.
 */

class BankersVisualizer {
  constructor() {
    this.matrices = null;
    this.bindEvents();
  }

  bindEvents() {
    // Run Safety Algorithm
    const runSafetyBtn = document.getElementById('btn-run-bankers-safety');
    if (runSafetyBtn) {
      runSafetyBtn.addEventListener('click', () => {
        this.runSafetyAlgorithm();
        if (window.app) window.app.playSound('success');
      });
    }

    // Deadlock Demo Buttons
    const triggerDeadlockBtn = document.getElementById('btn-trigger-intersection-deadlock');
    const resolveDeadlockBtn = document.getElementById('btn-resolve-intersection-deadlock');
    if (triggerDeadlockBtn) {
      triggerDeadlockBtn.addEventListener('click', () => {
        this.triggerIntersectionDeadlock();
      });
    }
    if (resolveDeadlockBtn) {
      resolveDeadlockBtn.addEventListener('click', () => {
        this.resolveIntersectionDeadlock();
      });
    }
  }

  async renderMatrices() {
    try {
      const res = await fetch(`${window.app.apiBase}/api/bankers/safety`);
      const data = await res.json();
      this.matrices = data.matrices;

      // Available Vector
      const availContainer = document.getElementById('bankers-available-vector');
      if (availContainer && data.matrices.available) {
        availContainer.innerHTML = data.matrices.available.map((val, idx) => `
          <div style="background: rgba(14, 19, 31, 0.85); border: 1px solid var(--border-subtle); padding: 12px 16px; border-radius: var(--radius-sm); text-align: center;">
            <div style="font-size: 0.68rem; color: var(--text-dim); font-family: var(--font-mono); text-transform: uppercase;">${data.matrices.resource_names[idx]}</div>
            <div style="font-family: var(--font-mono); font-size: 1.6rem; font-weight: 800; color: var(--color-cyan); margin-top: 4px;">${val}</div>
          </div>
        `).join('');
      }

      // Matrix Tables: Allocation, Max, Need
      this.renderMatrixTable('bankers-allocation-tbody', data.matrices.allocation, data.matrices.process_names);
      this.renderMatrixTable('bankers-max-tbody', data.matrices.max, data.matrices.process_names);
      this.renderMatrixTable('bankers-need-tbody', data.matrices.need, data.matrices.process_names);

      // Display initial safe sequence if available
      this.displaySafeSequenceResult(data);

    } catch (e) {
      console.warn('Bankers render error', e);
    }
  }

  renderMatrixTable(elementId, matrix, processNames) {
    const tbody = document.getElementById(elementId);
    if (!tbody || !matrix) return;

    tbody.innerHTML = matrix.map((row, pIdx) => `
      <tr>
        <td style="font-weight: 700; color: #a5b4fc; text-align: left;">${processNames[pIdx]}</td>
        ${row.map(val => `<td style="font-family: var(--font-mono);">${val}</td>`).join('')}
      </tr>
    `).join('');
  }

  displaySafeSequenceResult(data) {
    const badgeContainer = document.getElementById('safe-sequence-badge-container');
    const traceBox = document.getElementById('bankers-trace-steps');
    if (!badgeContainer) return;

    if (data.is_safe) {
      badgeContainer.innerHTML = `
        <div style="padding: 14px 18px; border-radius: var(--radius-md); background: rgba(16, 231, 97, 0.1); border: 1px solid var(--color-lime); display: flex; align-items: center; justify-content: space-between;">
          <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.2rem;">🛡️</span>
            <div>
              <div style="font-weight: 800; color: #fff; font-size: 0.9rem;">SAFE EXECUTION STATE VERIFIED</div>
              <div style="font-size: 0.75rem; color: var(--text-muted);">All pending resource requests can be satisfied without deadlock risk.</div>
            </div>
          </div>
          <div style="font-family: var(--font-mono); font-size: 0.9rem; font-weight: 700; color: var(--color-lime); background: rgba(0,0,0,0.4); padding: 6px 14px; border-radius: var(--radius-xs); border: 1px solid rgba(16, 231, 97, 0.3);">
            &lt; ${data.safe_sequence_string} &gt;
          </div>
        </div>
      `;
    } else {
      badgeContainer.innerHTML = `
        <div style="padding: 14px 18px; border-radius: var(--radius-md); background: rgba(239, 68, 68, 0.1); border: 1px solid var(--color-rose); display: flex; align-items: center; justify-content: space-between;">
          <div>
            <div style="font-weight: 800; color: var(--color-rose);">⚠️ SYSTEM IN UNSAFE STATE</div>
            <div style="font-size: 0.75rem; color: #fca5a5;">Deadlock risk imminent! No valid execution sequence guarantees completion.</div>
          </div>
        </div>
      `;
    }

    if (traceBox && data.trace_steps) {
      traceBox.innerHTML = data.trace_steps.map(step => `
        <div style="display: flex; align-items: center; gap: 10px; padding: 8px 12px; background: rgba(255,255,255,0.02); border-left: 3px solid ${step.condition_met ? 'var(--color-lime)' : 'var(--color-rose)'}; margin-bottom: 4px; border-radius: 4px; font-size: 0.76rem; font-family: var(--font-mono);">
          <span style="color: ${step.condition_met ? 'var(--color-lime)' : 'var(--color-rose)'}; font-weight: 800; min-width: 16px;">${step.condition_met ? '✓' : '✗'}</span>
          <span style="color: #fff; font-weight: 700;">${step.name}</span>
          <span style="color: var(--text-dim); flex: 1;">${step.action}</span>
          <span style="color: var(--color-cyan);">Work: [${step.work_after.join(', ')}]</span>
        </div>
      `).join('');
    }
  }

  async runSafetyAlgorithm() {
    if (window.app) {
      window.app.showToast('Evaluating Safety', "Running Dijkstra's Banker's Algorithm to find Safe Execution Sequence...", 'info');
    }
    await this.renderMatrices();
  }

  async triggerIntersectionDeadlock() {
    const badgeContainer = document.getElementById('safe-sequence-badge-container');
    const nodes = ['Car_A', 'Car_B', 'Car_C', 'Car_D', 'Ramp_North', 'Ramp_East', 'Ramp_South', 'Ramp_West'];
    const edges = [
      ['Car_A', 'Ramp_North'], ['Ramp_North', 'Car_B'],
      ['Car_B', 'Ramp_East'], ['Ramp_East', 'Car_C'],
      ['Car_C', 'Ramp_South'], ['Ramp_South', 'Car_D'],
      ['Car_D', 'Ramp_West'], ['Ramp_West', 'Car_A']
    ];

    try {
      const res = await fetch(`${window.app.apiBase}/api/bankers/rag`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nodes, edges })
      });
      const data = await res.json();

      if (badgeContainer) {
        badgeContainer.innerHTML = `
          <div style="padding: 16px 20px; border-radius: var(--radius-md); background: rgba(239, 68, 68, 0.15); border: 1px solid var(--color-rose); color: #fff;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
              <strong style="font-size: 0.95rem; color: #f87171;">🚨 DEADLOCK DETECTED IN RESOURCE ALLOCATION GRAPH!</strong>
              <span class="chip-val" style="color: var(--color-rose); font-size: 0.72rem;">CIRCULAR WAIT CYCLE FOUND</span>
            </div>
            <p style="font-size: 0.78rem; color: var(--text-muted); font-family: var(--font-mono); margin-bottom: 8px;">
              Cycle: <code style="color: var(--color-amber);">${data.cycle_summary}</code>
            </p>
            <div style="font-size: 0.74rem; color: #cbd5e1; display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; font-family: var(--font-mono);">
              <div>• Mutual Exclusion: <strong>SATISFIED</strong></div>
              <div>• Hold and Wait: <strong>SATISFIED</strong></div>
              <div>• No Preemption: <strong>SATISFIED</strong></div>
              <div>• Circular Wait: <strong style="color: var(--color-rose);">ACTIVE CYCLE!</strong></div>
            </div>
          </div>
        `;
      }
      if (window.app) {
        window.app.playSound('alarm');
        window.app.showToast('Gridlock Deadlock', 'All 4 Coffman conditions satisfied! Circular wait created.', 'error');
      }
    } catch (e) {
      console.warn('RAG error', e);
    }
  }

  resolveIntersectionDeadlock() {
    const badgeContainer = document.getElementById('safe-sequence-badge-container');
    if (badgeContainer) {
      badgeContainer.innerHTML = `
        <div style="padding: 14px 18px; border-radius: var(--radius-md); background: rgba(16, 231, 97, 0.15); border: 1px solid var(--color-lime); color: #fff;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
            <strong style="font-size: 0.9rem; color: var(--color-lime);">🛡️ DEADLOCK RESOLVED VIA PREEMPTION</strong>
            <span class="chip-val" style="color: var(--color-lime); font-size: 0.72rem;">CIRCULAR WAIT BROKEN</span>
          </div>
          <p style="font-size: 0.75rem; color: var(--text-muted);">Preempted resource held by Car_D. Circular wait broken. Remaining vehicles cleared intersection in order: Car_C &rarr; Car_B &rarr; Car_A.</p>
        </div>
      `;
    }
    if (window.app) {
      window.app.playSound('success');
      window.app.showToast('Deadlock Cleared', 'Resource preemption broke circular wait cycle.', 'success');
    }
  }
}

window.BankersVisualizer = BankersVisualizer;
