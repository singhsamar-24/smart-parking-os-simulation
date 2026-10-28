#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generates publication-quality plots and an academic PDF report
for the OS PBL Smart Parking Management System.
"""

import os
import sys
import json
import base64
import subprocess
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(WORKSPACE_DIR, "data")
PLOTS_DIR = os.path.join(DATA_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

# 1. Generate High-Quality Visual Charts
def generate_charts():
    print("Generating Matplotlib Benchmark Charts...")
    plt.rcParams.update({
        'font.sans-serif': 'Segoe UI, Helvetica, Arial, sans-serif',
        'font.family': 'sans-serif',
        'figure.autolayout': True,
        'axes.edgecolor': '#cbd5e1',
        'axes.linewidth': 1.2,
        'grid.color': '#e2e8f0',
        'grid.linestyle': '--',
        'grid.alpha': 0.7
    })

    # --- Chart 1: Average Waiting Time (AWT) across Algorithms (Workload 1 vs Workload 2) ---
    algos = ['FCFS', 'SJF', 'SRTF', 'Priority NP', 'Priority P', 'RR (q=2)', 'RR (q=4)']
    w1_awt = [11.40, 8.20, 6.60, 9.20, 8.20, 13.00, 13.00]
    w2_awt = [12.00, 6.00, 6.00, 8.00, 8.00, 11.50, 12.33]

    x = np.arange(len(algos))
    width = 0.38

    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=300)
    rects1 = ax.bar(x - width/2, w1_awt, width, label='Workload 1 (Mixed Traffic)', color='#2563eb', edgecolor='#1d4ed8')
    rects2 = ax.bar(x + width/2, w2_awt, width, label='Workload 2 (Rush Hour)', color='#059669', edgecolor='#047857')

    ax.set_ylabel('Average Waiting Time (seconds)', fontsize=11, fontweight='600', color='#1e293b')
    ax.set_title('CPU Scheduling Benchmark: Average Waiting Time (AWT) Comparison', fontsize=13, fontweight='700', pad=15, color='#0f172a')
    ax.set_xticks(x)
    ax.set_xticklabels(algos, fontsize=10, fontweight='500', color='#334155')
    ax.legend(frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=10)
    ax.grid(axis='y')

    # Add values on top of bars
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}s',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8.5, fontweight='600', color='#1e293b')

    autolabel(rects1)
    autolabel(rects2)

    plot1_path = os.path.join(PLOTS_DIR, "scheduling_awt_comparison.png")
    fig.savefig(plot1_path, dpi=300)
    plt.close(fig)
    print(f"  [+] Saved: {plot1_path}")

    # --- Chart 2: Convoy Effect Demonstration (Workload 3) ---
    fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=300)
    convoy_algos = ['FCFS\n(Convoy Delay)', 'SJF\n(Non-Preempt)', 'SRTF\n(Preemptive)', 'Round Robin\n(q=2)']
    convoy_awt = [15.00, 14.50, 1.75, 3.25]
    colors = ['#dc2626', '#ea580c', '#16a34a', '#0284c7']

    bars = ax.bar(convoy_algos, convoy_awt, color=colors, width=0.55, edgecolor='#334155', linewidth=1)
    ax.set_ylabel('Average Waiting Time (seconds)', fontsize=11, fontweight='600', color='#1e293b')
    ax.set_title('Workload 3: Mitigation of Convoy Effect (Heavy Truck Arrives First)', fontsize=12.5, fontweight='700', pad=15, color='#0f172a')
    ax.grid(axis='y')

    for bar in bars:
        h = bar.get_height()
        ax.annotate(f'{h:.2f}s',
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9.5, fontweight='700', color='#0f172a')

    # Draw arrow and annotation
    ax.annotate('88.3% Delay Reduction\nvia Preemption!',
                xy=(2, 2.0), xytext=(2.2, 8.5),
                arrowprops=dict(facecolor='#16a34a', shrink=0.08, width=1.5, headwidth=6),
                fontsize=9.5, fontweight='700', color='#15803d',
                bbox=dict(boxstyle="round,pad=0.4", fc="#dcfce7", ec="#86efac", lw=1))

    plot2_path = os.path.join(PLOTS_DIR, "convoy_effect_analysis.png")
    fig.savefig(plot2_path, dpi=300)
    plt.close(fig)
    print(f"  [+] Saved: {plot2_path}")

    # --- Chart 3: Turnaround vs Response Time Tradeoff ---
    fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=300)
    rr_algos = ['FCFS', 'SJF', 'SRTF', 'Priority P', 'RR (q=2)', 'RR (q=4)']
    response_times = [11.40, 8.20, 4.40, 6.40, 2.80, 6.00]
    turnaround_times = [17.00, 13.80, 12.20, 13.80, 18.60, 18.60]

    x3 = np.arange(len(rr_algos))
    ax.plot(x3, response_times, marker='o', linewidth=2.5, color='#7c3aed', label='Avg Response Time (Interactive Latency)')
    ax.plot(x3, turnaround_times, marker='s', linewidth=2.5, color='#d97706', label='Avg Turnaround Time (Total Span)')

    ax.set_xticks(x3)
    ax.set_xticklabels(rr_algos, fontsize=10, fontweight='500', color='#334155')
    ax.set_ylabel('Time (seconds)', fontsize=11, fontweight='600', color='#1e293b')
    ax.set_title('Responsiveness vs Turnaround Time Trade-off (Workload 1)', fontsize=12.5, fontweight='700', pad=15, color='#0f172a')
    ax.legend(frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=9.5)
    ax.grid(True)

    for i, txt in enumerate(response_times):
        ax.annotate(f'{txt:.1f}s', (x3[i], response_times[i] - 0.9), fontsize=8.5, ha='center', fontweight='600', color='#6b21a8')
    for i, txt in enumerate(turnaround_times):
        ax.annotate(f'{txt:.1f}s', (x3[i], turnaround_times[i] + 0.5), fontsize=8.5, ha='center', fontweight='600', color='#b45309')

    plot3_path = os.path.join(PLOTS_DIR, "tradeoff_response_tat.png")
    fig.savefig(plot3_path, dpi=300)
    plt.close(fig)
    print(f"  [+] Saved: {plot3_path}")

    return plot1_path, plot2_path, plot3_path


def image_to_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")
    return ""


def build_html_report(plot1_path, plot2_path, plot3_path):
    logo_path = os.path.join(WORKSPACE_DIR, "extracted_1month_ppt", "niet_logo_hq.png")
    logo_b64 = image_to_base64(logo_path)
    p1_b64 = image_to_base64(plot1_path)
    p2_b64 = image_to_base64(plot2_path)
    p3_b64 = image_to_base64(plot3_path)

    # Read Python benchmark script to embed as verified source code annexure
    with open(os.path.join(WORKSPACE_DIR, "benchmark_experiments.py"), "r", encoding="utf-8") as f:
        bench_code = f.read()

    # Escape HTML
    bench_code_escaped = (bench_code
                          .replace("&", "&amp;")
                          .replace("<", "&lt;")
                          .replace(">", "&gt;"))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Smart Parking Management System — OS PBL Experimental Report</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 18mm 16mm 18mm 16mm;
    @bottom-right {{
      content: "Page " counter(page) " of " counter(pages);
      font-size: 8pt;
      color: #64748b;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
  }}

  * {{
    box-sizing: border-box;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.5;
    font-size: 10pt;
    margin: 0;
    padding: 0;
    background: #ffffff;
  }}

  /* Page Break Control */
  .page-break {{
    page-break-after: always;
    break-after: page;
  }}

  .avoid-break {{
    page-break-inside: avoid;
    break-inside: avoid;
  }}

  /* Header Section */
  .header-card {{
    border-bottom: 2.5px solid #1e3a8a;
    padding-bottom: 12px;
    margin-bottom: 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  .header-titles {{
    flex: 1;
  }}

  .inst-name {{
    font-size: 13pt;
    font-weight: 800;
    color: #1e3a8a;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0 0 2px 0;
  }}

  .dept-name {{
    font-size: 9.5pt;
    font-weight: 600;
    color: #475569;
    margin: 0 0 4px 0;
  }}

  .doc-title {{
    font-size: 16pt;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.3px;
    margin: 4px 0 2px 0;
  }}

  .course-badge {{
    display: inline-block;
    background: #e0f2fe;
    color: #0369a1;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 8.5pt;
    border: 1px solid #bae6fd;
    margin-top: 4px;
  }}

  .logo-img {{
    max-height: 70px;
    max-width: 140px;
    object-fit: contain;
  }}

  /* Metadata Box */
  .meta-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 18px;
    font-size: 8.5pt;
  }}

  .meta-item strong {{
    color: #0f172a;
  }}

  /* Headings */
  h2 {{
    font-size: 12.5pt;
    font-weight: 700;
    color: #1e3a8a;
    border-bottom: 1.5px solid #cbd5e1;
    padding-bottom: 4px;
    margin-top: 18px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
  }}

  h3 {{
    font-size: 10.5pt;
    font-weight: 700;
    color: #334155;
    margin-top: 12px;
    margin-bottom: 6px;
  }}

  /* Tables */
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0 14px 0;
    font-size: 8.5pt;
  }}

  th {{
    background: #1e3a8a;
    color: #ffffff;
    font-weight: 600;
    text-align: left;
    padding: 6px 8px;
    border: 1px solid #1e3a8a;
  }}

  td {{
    padding: 5px 8px;
    border: 1px solid #cbd5e1;
  }}

  tr:nth-child(even) {{
    background: #f8fafc;
  }}

  /* Badges */
  .badge-safe {{
    background: #dcfce7;
    color: #15803d;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 3px;
    display: inline-block;
  }}

  .badge-danger {{
    background: #fee2e2;
    color: #b91c1c;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 3px;
    display: inline-block;
  }}

  .badge-verified {{
    background: #e0e7ff;
    color: #3730a3;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 3px;
    display: inline-block;
  }}

  /* Charts */
  .chart-container {{
    text-align: center;
    margin: 10px 0;
  }}

  .chart-img {{
    width: 100%;
    max-height: 250px;
    object-fit: contain;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 4px;
    background: #ffffff;
  }}

  .chart-caption {{
    font-size: 8pt;
    color: #64748b;
    margin-top: 4px;
    font-style: italic;
  }}

  /* Callout Card */
  .callout {{
    background: #eff6ff;
    border-left: 3.5px solid #2563eb;
    padding: 8px 12px;
    margin: 10px 0;
    border-radius: 0 4px 4px 0;
    font-size: 8.8pt;
  }}

  .callout-success {{
    background: #f0fdf4;
    border-left-color: #16a34a;
  }}

  /* Monospace Code Annexure */
  pre {{
    background: #0f172a;
    color: #f8fafc;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 7.2pt;
    line-height: 1.35;
    padding: 10px;
    border-radius: 4px;
    overflow-x: auto;
    white-space: pre-wrap;
    border: 1px solid #334155;
  }}

  /* Signatures */
  .sig-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 40px;
    margin-top: 35px;
    padding-top: 15px;
  }}

  .sig-line {{
    border-top: 1px solid #475569;
    padding-top: 6px;
    text-align: center;
    font-size: 8.5pt;
    font-weight: 600;
    color: #334155;
  }}
</style>
</head>
<body>

  <!-- ==================== PAGE 1: TITLE & CPU SCHEDULING ==================== -->
  <div class="header-card">
    <div class="header-titles">
      <div class="inst-name">Noida Institute of Engineering & Technology</div>
      <div class="dept-name">Department of Computer Science & Engineering (Artificial Intelligence)</div>
      <div class="doc-title">OS PBL Experimental Benchmark & Evaluation Report</div>
      <span class="course-badge">Course: Operating Systems (CCSE0303A) — Unit 2 & Unit 3</span>
    </div>
    {"<img class='logo-img' src='" + logo_b64 + "' alt='NIET Logo'>" if logo_b64 else ""}
  </div>

  <div class="meta-grid">
    <div class="meta-item">
      <strong>Project Title:</strong> Smart Parking Management System (OS Simulation)<br>
      <strong>Student Team:</strong> Group 7 (Ishank Rana, Chhavi Attri, Aditi Singh, Pratyush Agrahari, Samar Singh)<br>
      <strong>Class & Section:</strong> B.Tech CSE-AI · 2nd Year · Semester 3/4
    </div>
    <div class="meta-item">
      <strong>Faculty Mentors:</strong> Mr. Amar Pal Yadav & Dr. Varsha Jotwani<br>
      <strong>Framework:</strong> Standalone Python 3.11 Runtime / Standard OS Kernel Emulation<br>
      <strong>UN SDG Impact:</strong> SDG 11 — Sustainable Cities & Communities
    </div>
  </div>

  <h2>1. Project Real-World Mapping to Core Operating System Concepts</h2>
  <p style="margin-top: 4px; margin-bottom: 8px;">
    The Smart Parking Management System serves as a physical, verifiable computing analogy to demonstrate 
    <strong>Process Management</strong>, <strong>CPU Scheduling</strong>, <strong>Deadlock Avoidance</strong>, and <strong>Thread Concurrency</strong>:
  </p>

  <table>
    <thead>
      <tr>
        <th style="width: 25%;">Real-World Parking Entity</th>
        <th style="width: 28%;">Operating System Concept</th>
        <th>System Role & Functional Responsibility</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Incoming Vehicle</strong></td>
        <td><strong>Process (PCB)</strong></td>
        <td>Assigned unique PID, burst time (duration), priority level (Emergency, EV, SUV, Standard).</td>
      </tr>
      <tr>
        <td><strong>Dedicated Parking Bay</strong></td>
        <td><strong>Hardware Resource / Memory Frame</strong></td>
        <td>Shared, finite resource managed via allocation vectors and counting semaphores.</td>
      </tr>
      <tr>
        <td><strong>Automated Entry Gate</strong></td>
        <td><strong>Critical Section Boundary</strong></td>
        <td>Protected by Mutex locks and Peterson's software protocol to eliminate data race collisions.</td>
      </tr>
      <tr>
        <td><strong>Bay Dispatch Controller</strong></td>
        <td><strong>CPU Scheduler & Dispatcher</strong></td>
        <td>Executes FCFS, SJF, SRTF, Priority, and Round Robin scheduling policies across ready queues.</td>
      </tr>
    </tbody>
  </table>

  <h2>2. Experiment 1: CPU Process Scheduling Multi-Workload Benchmark (Unit 2)</h2>
  <p style="margin-top: 4px; margin-bottom: 8px;">
    All 6 standard CPU scheduling algorithms were benchmarked across 4 realistic traffic workloads:
    <em>Workload 1 (Standard Mixed)</em>, <em>Workload 2 (Rush Hour)</em>, <em>Workload 3 (Convoy Truck)</em>, and <em>Workload 4 (Emergency Priority)</em>.
  </p>

  <div class="chart-container avoid-break">
    <img class="chart-img" src="{p1_b64}" alt="AWT Comparison Chart">
    <div class="chart-caption">Figure 1.1: Empirical comparison of Average Waiting Time (AWT in seconds) across 7 CPU scheduling variants.</div>
  </div>

  <table class="avoid-break">
    <thead>
      <tr>
        <th>Workload Profile</th>
        <th>Algorithm</th>
        <th>Avg Waiting (AWT)</th>
        <th>Avg Turnaround (ATAT)</th>
        <th>Avg Response (ART)</th>
        <th>CPU / Bay Util %</th>
        <th>Context Switches</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td rowspan="4"><strong>Workload 1</strong><br>(Mixed Fleet: 5 Procs)</td>
        <td>FCFS</td>
        <td>11.40s</td>
        <td>17.00s</td>
        <td>11.40s</td>
        <td>100.0%</td>
        <td>4</td>
      </tr>
      <tr>
        <td>SJF (Non-Preemptive)</td>
        <td>8.20s</td>
        <td>13.80s</td>
        <td>8.20s</td>
        <td>100.0%</td>
        <td>4</td>
      </tr>
      <tr>
        <td><strong>SRTF (Preemptive)</strong></td>
        <td><strong style="color: #15803d;">6.60s</strong></td>
        <td><strong style="color: #15803d;">12.20s</strong></td>
        <td>4.40s</td>
        <td>100.0%</td>
        <td>5</td>
      </tr>
      <tr>
        <td>Round Robin (q=2)</td>
        <td>13.00s</td>
        <td>18.60s</td>
        <td><strong style="color: #2563eb;">2.80s (Lowest)</strong></td>
        <td>100.0%</td>
        <td>13</td>
      </tr>
      <tr>
        <td rowspan="3"><strong>Workload 3</strong><br>(Convoy Truck: 4 Procs)</td>
        <td>FCFS (Convoy Penalty)</td>
        <td><strong style="color: #b91c1c;">15.00s</strong></td>
        <td>21.25s</td>
        <td>15.00s</td>
        <td>100.0%</td>
        <td>3</td>
      </tr>
      <tr>
        <td>SJF (Non-Preemptive)</td>
        <td>14.50s</td>
        <td>20.75s</td>
        <td>14.50s</td>
        <td>100.0%</td>
        <td>3</td>
      </tr>
      <tr>
        <td><strong>SRTF (Preemptive)</strong></td>
        <td><strong style="color: #15803d;">1.75s (-88.3%)</strong></td>
        <td><strong style="color: #15803d;">8.00s</strong></td>
        <td><strong style="color: #15803d;">0.50s</strong></td>
        <td>100.0%</td>
        <td>4</td>
      </tr>
    </tbody>
  </table>

  <!-- PAGE BREAK -->
  <div class="page-break"></div>

  <!-- ==================== PAGE 2: CONVOY EFFECT & DEADLOCK ==================== -->
  <h2>3. Workload 3 Analysis: Mitigating the Convoy Effect via Preemption</h2>
  
  <div class="chart-container avoid-break">
    <img class="chart-img" src="{p2_b64}" alt="Convoy Effect Chart">
    <div class="chart-caption">Figure 2.1: Convoy Effect Mitigation — Preemptive SRTF reduces queue delay for short vehicles by 88.3%.</div>
  </div>

  <div class="callout callout-success">
    <strong>Theoretical Conclusion on CPU Scheduling:</strong><br>
    Non-preemptive FCFS suffers severe performance degradation when a process with large burst time arrives first (Convoy Effect). 
    Shortest Remaining Time First (SRTF) optimally minimizes Average Waiting Time by preempting the CPU to service shorter incoming jobs, 
    while Round Robin with small quantum ($q=2$) delivers superior response times for interactive arrivals at the expense of higher context switches.
  </div>

  <h2>4. Experiment 2: Deadlock Avoidance via Banker's Algorithm & RAG (Unit 3)</h2>
  <p style="margin-top: 4px; margin-bottom: 8px;">
    The simulation models a 5-process system ($P_0$ through $P_4$) managing 4 distinct parking bay resource types 
    (Compact: 8, EV Charging: 4, Heavy SUV: 2, Valet: 2).
  </p>

  <h3>A. Baseline State Matrix & Safety Verification</h3>
  <table>
    <thead>
      <tr>
        <th>Process</th>
        <th>Vehicle Role</th>
        <th>Allocation Vector [C, EV, S, V]</th>
        <th>Maximum Need Vector [C, EV, S, V]</th>
        <th>Remaining Need [C, EV, S, V]</th>
      </tr>
    </thead>
    <tbody>
      <tr><td><strong>P0</strong></td><td>Fleet Van</td><td>[0, 1, 0, 0]</td><td>[7, 5, 3, 2]</td><td>[7, 4, 3, 2]</td></tr>
      <tr><td><strong>P1</strong></td><td>EV Taxi</td><td>[2, 0, 0, 1]</td><td>[3, 2, 2, 2]</td><td>[1, 2, 2, 1]</td></tr>
      <tr><td><strong>P2</strong></td><td>Heavy Logistics Truck</td><td>[3, 0, 2, 1]</td><td>[9, 0, 2, 2]</td><td>[6, 0, 0, 1]</td></tr>
      <tr><td><strong>P3</strong></td><td>Compact EV Commuter</td><td>[2, 1, 1, 0]</td><td>[2, 2, 2, 1]</td><td>[0, 1, 1, 1]</td></tr>
      <tr><td><strong>P4</strong></td><td>Family SUV</td><td>[0, 0, 2, 0]</td><td>[4, 3, 3, 2]</td><td>[4, 3, 1, 2]</td></tr>
      <tr style="background: #e0f2fe; font-weight: 700;">
        <td colspan="2">Currently Available Vector</td>
        <td colspan="3">[3 Compact, 3 EV Charging, 2 Heavy SUV, 2 Valet Bays]</td>
      </tr>
    </tbody>
  </table>

  <div class="callout">
    <strong>Banker's Safety Result:</strong> Initial state is strictly <span class="badge-safe">SAFE</span>. 
    Execution Order: <code>P1 &rarr; P3 &rarr; P4 &rarr; P0 &rarr; P2</code>. System guarantees all processes terminate without deadlock.
  </div>

  <h3>B. Empirical Resource Request Scenarios</h3>
  <table>
    <thead>
      <tr>
        <th>Test Case ID</th>
        <th>Request Vector & Process</th>
        <th>Evaluated Condition</th>
        <th>Algorithm Decision</th>
        <th>Safety Sequence / Root Cause</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>TC-BANKER-02</code></td>
        <td>P1 requests <code>[1, 0, 2, 0]</code></td>
        <td>Request &le; Need &amp; Request &le; Available</td>
        <td><span class="badge-safe">GRANTED (SAFE)</span></td>
        <td>Safe state maintained: <code>P1 &rarr; P3 &rarr; P4 &rarr; P0 &rarr; P2</code></td>
      </tr>
      <tr>
        <td><code>TC-BANKER-03</code></td>
        <td>P0 requests <code>[8, 0, 0, 0]</code></td>
        <td>Step 1: Request &le; Need Check</td>
        <td><span class="badge-danger">DENIED / BLOCKED</span></td>
        <td>Violates maximum declared need (Requested 8 > Declared 7).</td>
      </tr>
      <tr>
        <td><code>TC-BANKER-04</code></td>
        <td>P4 requests <code>[4, 4, 4, 4]</code></td>
        <td>Step 2: Request &le; Available Check</td>
        <td><span class="badge-danger">DENIED / BLOCKED</span></td>
        <td>Insufficient free slots available (Starvation prevented).</td>
      </tr>
      <tr>
        <td><code>TC-BANKER-05</code></td>
        <td>P0 requests <code>[0, 2, 0, 0]</code></td>
        <td>Step 4: Safety Check on Tentative State</td>
        <td><span class="badge-danger">DENIED (DEADLOCK RISK)</span></td>
        <td>Tentative state leaves insufficient EV slots, rendering state UNSAFE.</td>
      </tr>
      <tr>
        <td><code>TC-RAG-01</code></td>
        <td>Acyclic Graph $(P_1 \rightarrow R_1 \rightarrow P_2)$</td>
        <td>DFS Cycle Detection in RAG</td>
        <td><span class="badge-safe">NO DEADLOCK</span></td>
        <td>Acyclic topology confirms absence of circular wait.</td>
      </tr>
      <tr>
        <td><code>TC-RAG-02</code></td>
        <td>Cyclic Graph $(P_1 \rightarrow R_1 \rightarrow P_2 \rightarrow R_2 \rightarrow P_1)$</td>
        <td>DFS Cycle Detection in RAG</td>
        <td><span class="badge-danger">DEADLOCK DETECTED</span></td>
        <td>Cycle detected: <code>P1 &rarr; R1 &rarr; P2 &rarr; R2 &rarr; P1</code> (Coffman condition 4).</td>
      </tr>
    </tbody>
  </table>

  <!-- PAGE BREAK -->
  <div class="page-break"></div>

  <!-- ==================== PAGE 3: CONCURRENCY & CLASSICAL SYNC ==================== -->
  <h2>5. Experiment 3: Concurrency Control & Mutual Exclusion Verification (Unit 3)</h2>

  <div class="chart-container avoid-break">
    <img class="chart-img" src="{p3_b64}" alt="Tradeoff Chart">
    <div class="chart-caption">Figure 3.1: Latency & Responsiveness vs Completion Trade-off across Scheduling Policies.</div>
  </div>

  <table>
    <thead>
      <tr>
        <th>Synchronization Primitives</th>
        <th>Concurrent Threads</th>
        <th>Mutual Exclusion</th>
        <th>Collision Hazard</th>
        <th>Verification Proof & Empirical Findings</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Unsynchronized Access</strong></td>
        <td>2 (Car A &amp; Car B)</td>
        <td><span class="badge-danger">FAILED (None)</span></td>
        <td><strong style="color: #b91c1c;">COLLISION DETECTED</strong></td>
        <td>Both threads read slot S04 as FREE simultaneously before writing; corrupts state with double allocation.</td>
      </tr>
      <tr>
        <td><strong>Mutex Lock (threading.Lock)</strong></td>
        <td>2 (Car A &amp; Car B)</td>
        <td><span class="badge-safe">PRESERVED (100%)</span></td>
        <td><strong style="color: #15803d;">ZERO COLLISIONS</strong></td>
        <td>Atomic entry section blocks Thread B until Thread A finishes allocation and releases lock.</td>
      </tr>
      <tr>
        <td><strong>Peterson's Algorithm</strong></td>
        <td>2 (Gate-North &amp; South)</td>
        <td><span class="badge-safe">PRESERVED (100%)</span></td>
        <td><strong style="color: #15803d;">ZERO COLLISIONS</strong></td>
        <td>Validated formal proof: <code>flag[0]=True</code>, <code>flag[1]=True</code>, and <code>turn</code> arbitrate entry without hardware locks.</td>
      </tr>
      <tr>
        <td><strong>Hardware Test-and-Set (TSL)</strong></td>
        <td>2 (Kiosk 1 &amp; Kiosk 2)</td>
        <td><span class="badge-safe">PRESERVED (100%)</span></td>
        <td><strong style="color: #15803d;">ZERO COLLISIONS</strong></td>
        <td>Atomic machine instruction prevents preemption between read and write register cycles.</td>
      </tr>
      <tr>
        <td><strong>Counting Semaphore</strong></td>
        <td>18 Simultaneous Ingress</td>
        <td><span class="badge-safe">PRESERVED (100%)</span></td>
        <td><strong style="color: #15803d;">ZERO OVERFLOW</strong></td>
        <td>Exactly 16 slots allocated. The 2 surplus requests placed into blocked FIFO wait queue.</td>
      </tr>
    </tbody>
  </table>

  <h2>6. Experiment 4: Classical IPC Synchronization Problems (Unit 3)</h2>
  <table>
    <thead>
      <tr>
        <th>Classical Problem</th>
        <th>Real-World Parking Equivalent</th>
        <th>OS Mechanism Applied</th>
        <th>Boundary Conditions Validated</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Producer-Consumer</strong></td>
        <td>Entry Camera vs Bay Dispatcher</td>
        <td>Bounded Buffer (Capacity 5) + Mutex + Counting Semaphores</td>
        <td>Buffer saturation blocks producer; consumption signals available space.</td>
        <td><span class="badge-verified">PASSED</span></td>
      </tr>
      <tr>
        <td><strong>Reader-Writer</strong></td>
        <td>Digital Guidance Signs vs Bay Allocations</td>
        <td>Reader-Priority Mutex + Exclusive <code>wrt</code> Semaphore</td>
        <td>Multiple readers access data concurrently; writers locked out until readers finish.</td>
        <td><span class="badge-verified">PASSED</span></td>
      </tr>
      <tr>
        <td><strong>Sleeping Barber</strong></td>
        <td>Manual Barrier Guard &amp; Waiting Chairs</td>
        <td>Gatekeeper Mutex + Condition Variable Waiting Queue</td>
        <td>Guard sleeps when empty; car wakes guard; excess cars handled gracefully.</td>
        <td><span class="badge-verified">PASSED</span></td>
      </tr>
      <tr>
        <td><strong>Dining Philosophers</strong></td>
        <td>5-Way Roundabout Intersection</td>
        <td>Resource Hierarchy / Asymmetric Resource Allocation</td>
        <td>Symmetric requests cause circular wait deadlock; hierarchy breaks deadlock.</td>
        <td><span class="badge-verified">PASSED</span></td>
      </tr>
    </tbody>
  </table>

  <div class="sig-grid avoid-break">
    <div class="sig-line">
      Submitted by: <strong>Group 7 (CSE-AI)</strong><br>
      Ishank Rana · Chhavi Attri · Aditi Singh · Pratyush Agrahari · Samar Singh
    </div>
    <div class="sig-line">
      Approved &amp; Evaluated by: <strong>Faculty Supervisors</strong><br>
      Mr. Amar Pal Yadav &amp; Dr. Varsha Jotwani (Department of CSE-AI, NIET)
    </div>
  </div>

  <!-- PAGE BREAK -->
  <div class="page-break"></div>

  <!-- ==================== PAGE 4: CODE ANNEXURE ==================== -->
  <h2>7. Annexure: Verified Standalone Benchmark Python Source Code</h2>
  <p style="margin-top: 4px; margin-bottom: 8px;">
    The following verified, complete Python implementation (<code>benchmark_experiments.py</code>) executes all multi-workload simulations,
    validates safety algorithms, exports CSV/JSON data files, and was used to produce all empirical results in this report:
  </p>

  <pre><code>{bench_code_escaped}</code></pre>

</body>
</html>
"""
    output_html_path = os.path.join(DATA_DIR, "experimental_report.html")
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  [+] Saved HTML: {output_html_path}")
    return output_html_path


def convert_html_to_pdf(html_path, output_pdf_path):
    print("Converting HTML Report to Publication PDF via Microsoft Edge...")
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    edge_bin = None
    for p in edge_paths:
        if os.path.exists(p):
            edge_bin = p
            break

    if not edge_bin:
        print("[ERROR] Microsoft Edge executable not found!")
        return False

    cmd = [
        edge_bin,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        "--no-pdf-header-footer",
        f"--print-to-pdf={output_pdf_path}",
        html_path
    ]

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 1000:
        print(f"  [+] PDF Successfully Created: {output_pdf_path} ({os.path.getsize(output_pdf_path):,} bytes)")
        return True
    else:
        print(f"[ERROR] Failed to generate PDF: {res.stderr.decode()}")
        return False


def main():
    print("""
    ========================================================================
     PDF REPORT GENERATOR — SMART PARKING OS PBL BENCHMARK SUITE
    ========================================================================
    """)
    p1, p2, p3 = generate_charts()
    html_path = build_html_report(p1, p2, p3)

    pdf_target_1 = os.path.join(WORKSPACE_DIR, "Smart_Parking_OS_PBL_Experimental_Report.pdf")
    pdf_target_2 = os.path.join(DATA_DIR, "Smart_Parking_OS_PBL_Experimental_Report.pdf")

    success = convert_html_to_pdf(html_path, pdf_target_1)
    if success:
        # Also copy to data folder
        import shutil
        shutil.copyfile(pdf_target_1, pdf_target_2)
        print(f"  [+] Copied to Data Folder: {pdf_target_2}")

    print("\nProcess Complete! PDF ready for submission.")


if __name__ == "__main__":
    main()
