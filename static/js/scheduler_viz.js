/**
 * Smart Parking Management System - CPU Scheduling Visualizer & Gantt Chart
 * Unit 2: Process & Thread Management - CPU Scheduling Algorithms
 * All time units are in MINUTES (parking duration).
 */

class SchedulerVisualizer {
  constructor() {
    this.currentAlgo = 'FCFS';
    this.quantum = 2.0;   // minutes
    this.comparisonData = null;
    this.palette = [
      '#4f46e5', '#06b6d4', '#10b981', '#f59e0b', '#ec4899',
      '#8b5cf6', '#3b82f6', '#14b8a6', '#f97316', '#64748b'
    ];
    this.bindEvents();
  }

  bindEvents() {
    // Algorithm pill selectors
    document.querySelectorAll('.algo-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        document.querySelectorAll('.algo-pill').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        this.currentAlgo = pill.getAttribute('data-algo');
        this.render();
        window.app.playSound('click');
      });
    });

    // RR Quantum slider (minutes)
    const qSlider = document.getElementById('rr-quantum-slider');
    const qVal    = document.getElementById('rr-quantum-val');
    if (qSlider && qVal) {
      qSlider.addEventListener('input', (e) => {
        this.quantum = parseFloat(e.target.value);
        qVal.innerText = `${this.quantum} min`;
        if (this.currentAlgo === 'ROUND_ROBIN') this.render();
      });
    }

    // Run benchmark button
    const benchBtn = document.getElementById('run-benchmark-btn');
    if (benchBtn) {
      benchBtn.addEventListener('click', () => {
        this.runFullBenchmark();
        window.app.playSound('success');
      });
    }
  }

  /**
   * Build the process dataset for the scheduler.
   * Uses parking_duration_min as the burst_time so all charts are in MINUTES.
   * Arrival times are normalized to index order (0, 1, 2, …) for a clean demo.
   */
  getProcessDataset() {
    if (window.app && window.app.state) {
      const live = [
        ...window.app.state.ready_queue,
        ...window.app.state.running_processes
      ];
      if (live.length >= 3) {
        return live.map((p, idx) => ({
          pid:          p.pid,
          plate:        p.plate,
          // Use parking_duration_min; fall back to burst_time/60 for any legacy data
          burst_time:   p.parking_duration_min != null
                          ? p.parking_duration_min
                          : parseFloat((p.burst_time / 60).toFixed(2)),
          arrival_time: idx,          // sequential arrivals for the demo chart
          priority:     p.priority,
          vehicle_type: p.vehicle_type,
          payment_mode: p.payment_mode || 'CASH'
        }));
      }
    }

    // Default benchmark dataset — durations in MINUTES, arrivals in MINUTES
    return [
      { pid: 'P1', plate: 'DL-01-A100',  arrival_time: 0, burst_time: 30, priority: 3, vehicle_type: 'STANDARD'  },
      { pid: 'P2', plate: 'AMB-101',     arrival_time: 2, burst_time: 15, priority: 1, vehicle_type: 'EMERGENCY' },
      { pid: 'P3', plate: 'EV-TESLA',    arrival_time: 5, burst_time: 45, priority: 2, vehicle_type: 'EV'        },
      { pid: 'P4', plate: 'SUV-THAR',    arrival_time: 6, burst_time: 20, priority: 3, vehicle_type: 'SUV'       },
      { pid: 'P5', plate: 'UP-16-C500',  arrival_time: 8, burst_time: 25, priority: 4, vehicle_type: 'STANDARD'  }
    ];
  }

  async render() {
    const processes = this.getProcessDataset();
    try {
      const res = await fetch(`${window.app.apiBase}/api/scheduler/compare`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ processes, time_quantum: this.quantum })
      });
      const data = await res.json();
      if (data.success) {
        this.comparisonData = data.comparison;
        this.renderSingleAlgorithm(this.currentAlgo);
        this.renderBenchmarkCards(data.comparison);
      }
    } catch (e) {
      console.warn('Scheduler viz fetch error', e);
    }
  }

  renderSingleAlgorithm(algoKey) {
    const keyMap = {
      FCFS:        'fcfs',
      SJF:         'sjf',
      SRTF:        'srtf',
      PRIORITY_NP: 'priority_np',
      PRIORITY_P:  'priority_p',
      ROUND_ROBIN: 'round_robin'
    };
    const resultKey = keyMap[algoKey] || 'fcfs';
    if (!this.comparisonData || !this.comparisonData[resultKey]) return;

    const result = this.comparisonData[resultKey];

    // 1. Gantt chart
    this.renderGanttChart(result.timeline, result.metrics.total_time);

    // 2. Summary metrics (all in minutes)
    document.getElementById('metric-avg-wt').innerText      = `${result.metrics.avg_waiting_time} min`;
    document.getElementById('metric-avg-tat').innerText     = `${result.metrics.avg_turnaround_time} min`;
    document.getElementById('metric-cpu-util').innerText    = `${result.metrics.cpu_utilization}%`;
    document.getElementById('metric-throughput').innerText  = `${result.metrics.throughput} vehicles/min`;

    // 3. Per-process table
    this.renderProcessTable(result.processes);
  }

  renderGanttChart(timeline, totalTime) {
    const track    = document.getElementById('gantt-timeline-track');
    const labelRow = document.getElementById('gantt-time-labels');
    if (!track || !labelRow) return;

    if (!timeline || timeline.length === 0 || totalTime === 0) {
      track.innerHTML    = '<div style="padding: 14px; color: var(--text-dim);">No execution timeline — click Run Benchmark first.</div>';
      labelRow.innerHTML = '';
      return;
    }

    // Colour map: consistent colour per PID
    const pidColor = {};
    let ci = 0;

    let trackHtml  = '';
    let labelsHtml = '';

    timeline.forEach(seg => {
      const dur = seg.end - seg.start;
      const pct = (dur / totalTime) * 100;

      if (seg.pid === 'IDLE') {
        trackHtml += `
          <div class="gantt-segment"
               style="width:${pct}%; background:rgba(75,85,99,0.3); color:var(--text-dim);"
               title="Idle (${seg.start.toFixed(1)}–${seg.end.toFixed(1)} min)">
            IDLE
          </div>`;
      } else {
        if (!pidColor[seg.pid]) {
          pidColor[seg.pid] = this.palette[ci++ % this.palette.length];
        }
        trackHtml += `
          <div class="gantt-segment"
               style="width:${pct}%; background:${pidColor[seg.pid]};"
               title="${seg.plate || seg.pid} [${seg.start.toFixed(1)}–${seg.end.toFixed(1)} min]">
            <span>${seg.pid}</span>
            <span style="font-size:0.65rem;opacity:0.85;">${dur.toFixed(1)} min</span>
          </div>`;
      }
    });

    // Time-tick labels (only show a sensible number of ticks to avoid clutter)
    const allPoints = [...new Set([0, ...timeline.map(s => s.start), ...timeline.map(s => s.end)])]
      .sort((a, b) => a - b);

    // Thin out ticks if there are too many
    const maxTicks = 12;
    const step = Math.ceil(allPoints.length / maxTicks);
    allPoints.forEach((t, i) => {
      if (i % step !== 0 && i !== allPoints.length - 1) return;
      const pos = (t / totalTime) * 100;
      labelsHtml += `<span style="position:absolute;left:${pos}%;transform:translateX(-50%);">${t.toFixed(0)}</span>`;
    });

    track.innerHTML    = trackHtml;
    labelRow.innerHTML = labelsHtml;
  }

  renderProcessTable(processes) {
    const tbody = document.getElementById('scheduler-table-tbody');
    if (!tbody || !processes) return;

    const list = Object.values(processes).sort((a, b) => a.arrival_time - b.arrival_time);
    tbody.innerHTML = list.map(p => `
      <tr>
        <td style="font-weight:700; color:#a5b4fc;">${p.pid}</td>
        <td>${p.plate}</td>
        <td>P${p.priority}</td>
        <td>${p.arrival_time} min</td>
        <td>${p.burst_time} min</td>
        <td style="color:var(--color-cyan);">${p.completion_time} min</td>
        <td style="color:var(--color-emerald);">${p.turnaround_time} min</td>
        <td style="color:var(--color-amber);">${p.waiting_time} min</td>
      </tr>
    `).join('');
  }

  renderBenchmarkCards(comparison) {
    const container = document.getElementById('benchmark-cards-container');
    if (!container || !comparison) return;

    const labels = {
      fcfs:        'FCFS — First Come First Serve',
      sjf:         'SJF — Shortest Job First',
      srtf:        'SRTF — Shortest Remaining Time',
      priority_np: 'Priority (Non-Preemptive)',
      priority_p:  'Priority (Preemptive)',
      round_robin: `Round Robin (q = ${this.quantum} min)`
    };

    // Best = lowest average waiting time
    const minWt = Math.min(...Object.values(comparison).map(c => c.metrics.avg_waiting_time));

    let html = '';
    for (const [key, data] of Object.entries(comparison)) {
      const isBest = Math.abs(data.metrics.avg_waiting_time - minWt) < 0.05;
      // Bar width: scale against the worst performer for visual contrast
      const maxWt  = Math.max(...Object.values(comparison).map(c => c.metrics.avg_waiting_time)) || 1;
      const wtPct  = Math.min(100, (data.metrics.avg_waiting_time / maxWt) * 100);

      html += `
        <div class="benchmark-card" style="${isBest ? 'border-color:var(--color-emerald);box-shadow:0 0 12px rgba(16,185,129,0.25);' : ''}">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <strong style="font-size:0.85rem;color:#fff;">${labels[key]}</strong>
            ${isBest ? '<span class="status-badge status-done">⚡ Best</span>' : ''}
          </div>
          <div style="font-size:0.78rem;color:var(--text-muted);margin-bottom:6px;">
            Avg Wait: <strong style="color:#67e8f9;">${data.metrics.avg_waiting_time} min</strong>
          </div>
          <div class="benchmark-bar-track">
            <div class="benchmark-bar-fill" style="width:${wtPct}%;background:${isBest ? '#10b981' : '#3b82f6'};"></div>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:0.72rem;color:var(--text-dim);margin-top:6px;">
            <span>Avg TAT: ${data.metrics.avg_turnaround_time} min</span>
            <span>CPU Util: ${data.metrics.cpu_utilization}%</span>
          </div>
        </div>`;
    }

    container.innerHTML = html;
  }

  updateFromLiveState(state) {
    if (!this.comparisonData) {
      this.render();
    }
  }

  async runFullBenchmark() {
    window.app.showToast('Benchmark Started', 'Running all 6 scheduling algorithms on the same vehicle workload…', 'info');
    await this.render();
    window.app.showToast('Benchmark Done', 'Gantt chart and comparison table updated!', 'success');
  }
}

// Instantiate on script load
window.schedulerViz = new SchedulerVisualizer();
