# 🚗 NEXUS-PARK — Smart Parking Management & OS Simulation System

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![OS Simulation](https://img.shields.io/badge/OS-Deadlock%20%7C%20Concurrency%20%7C%20Scheduling-darkcyan.svg)](backend/)
[![UI: Real-Time Web](https://img.shields.io/badge/UI-Interactive%20Glassmorphic%20Dashboard-green.svg)](static/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Academic Project](https://img.shields.io/badge/NIET-OS%20PBL%20Group%207-blueviolet.svg)](docs/)
[![SDG](https://img.shields.io/badge/SDG%2011-Sustainable%20Cities-orange.svg)](https://sdgs.un.org/goals/goal11)

An interactive, production-grade Operating Systems capstone platform that bridges theoretical OS synchronization and resource allocation principles with real-world automated smart parking infrastructure.

Developed for the **Operating Systems (CCSE0303A)** curriculum at **Noida Institute of Engineering & Technology (NIET)** by **Group 7**.

---

## 🏛️ Operating System Concepts Mapped to Smart Parking

| Operating System Paradigm | Real-World Smart Parking Analogy | Implementation Module | Technical Significance |
|---|---|---|---|
| **Deadlock Avoidance** | Safe multi-resource allocation (Parking Bays, EV Chargers, Valet Drivers) | `backend/bankers.py` | Implements Dijkstra's **Banker's Algorithm** with safety sequence verification and request validation ($O(M \times N^2)$). Prevents gridlocks before allocating bays. |
| **Classical Concurrency** | Ingress/Egress boom barriers, ticket booth access, sensor updates | `backend/classical.py` | Models **Dining Philosophers** (adjacent bay sharing), **Producer-Consumer** (car arrival queue vs bay assignment), and **Reader-Writer** (real-time display boards vs slot updates). |
| **Process Scheduling** | Vehicle queue processing & priority lane dispatching | `backend/scheduler.py` | Simulates **FCFS**, **SJF (Shortest Job First)**, **Priority Scheduling** (EV/VIP/Ambulance), **Round Robin (RR)**, and **SRTF**. Computes turnaround and wait times. |
| **Thread Synchronization** | Multi-gate barrier concurrency & slot race conditions | `backend/concurrency.py` | Compares unprotected race conditions against Mutex (`threading.Lock`), Semaphores (`threading.Semaphore`), and Atomic CAS primitives. |

---

## ⚡ System Architecture

```
   +-------------------------------------------------------------+
   |            NEXUS-PARK Interactive Web Dashboard             |
   |   (Glassmorphic UI, Live Lot Matrix, Visual Lab Consoles)   |
   +------------------------------+------------------------------+
                                  |
                                  v
   +-------------------------------------------------------------+
   |             HTTP REST Ingress & Dispatcher API              |
   |              (Built-in Python HTTP Server)                  |
   +----+-------------------------+-------------------------+----+
        |                         |                         |
        v                         v                         v
+------------------+     +------------------+     +------------------+
| Banker's Engine  |     | Concurrency Lab  |     | CPU Scheduler    |
| - Safety State   |     | - Mutex / Locks  |     | - FCFS & SJF     |
| - Resource Vector|     | - Semaphores     |     | - Priority & RR  |
| - Safe Sequence  |     | - Dining Philos. |     | - Gantt Charts   |
+------------------+     +------------------+     +------------------+
        |                         |                         |
        +-------------------------+-------------------------+
                                  |
                                  v
   +-------------------------------------------------------------+
   |             Core SmartParkingSystem Controller              |
   | - 16 Smart Parking Bays (Regular, EV Charging, Handicapped) |
   | - Automated Billing Engine & Dynamic Tariffs                |
   | - Reservation & Maintenance Orchestrator                    |
   +-------------------------------------------------------------+
```

---

## 📂 Project Directory Structure

```
smart-parking-os-simulation/
├── backend/                                 # Core OS algorithm implementations
│   ├── bankers.py                           # Banker's algorithm for deadlock avoidance
│   ├── classical.py                         # Classical synchronization problems
│   ├── concurrency.py                       # Thread locking, semaphores, race tests
│   ├── models.py                            # Data models (Vehicle, Slot, Reservation)
│   ├── parking_system.py                    # Master state machine & business logic
│   └── scheduler.py                         # FCFS, SJF, Priority, RR algorithms
├── data/                                    # Benchmarking results & datasets
│   ├── plots/                               # Generated performance comparison plots
│   ├── concurrency_benchmark_results.csv    # Lock vs No-Lock benchmark data
│   ├── scheduling_benchmark_results.csv     # Turnaround & wait time logs
│   ├── deadlock_safety_results.csv          # Safe sequence test logs
│   ├── EXPERIMENT_RESULTS_REPORT.md         # Exhaustive benchmark report
│   └── master_experimental_dataset.json     # Master JSON test corpus
├── docs/                                    # Formal reports & academic deliverables
│   ├── Final Report.docx                    # Final comprehensive project report
│   ├── Group_7_Progress_Report_Month_2_Detailed.docx
│   ├── Smart Parking Management System.pdf
│   ├── Smart_Parking_Management_System_OS_PBL.pdf
│   ├── Smart_Parking_Management_System_OS_PBL.pptx
│   ├── Smart_Parking_OS_PBL_Experimental_Report.pdf
│   ├── Smart_Parking_OS_Full_Report.md
│   ├── OS_Lab_Manual_Samar_Singh.docx
│   └── os.docx
├── exported_slides/                         # Rendered presentation slides (PNG)
├── extracted_1month_ppt/                    # Brand assets & institutional crests
├── static/                                  # Real-time web user interface
│   ├── css/                                 # Glassmorphic responsive styling
│   ├── js/                                  # Canvas charts, state pollers, modules
│   └── index.html                           # Single-page operations portal
├── tests/
│   └── test_saas_integration.py             # 11-step backend & DOM integrity suite
├── .gitignore                               # Standard gitignore
├── LICENSE                                  # MIT License
├── README.md                                # Platform documentation
├── benchmark_experiments.py                 # Automated benchmark test suite
├── main.py                                  # Web server & API entry point
├── run_experiments.bat                      # Windows one-click benchmark script
└── run_system.bat                           # Windows one-click launch script
```

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
- Python 3.10 or higher
- Standard library only (no external dependencies needed to run the server or dashboard)

### 2. Launch the System

**Option A: Windows Batch Launcher (Recommended)**
Double click or run:
```cmd
run_system.bat
```

**Option B: Terminal Command**
```bash
python main.py
```
Then navigate your browser to `http://127.0.0.1:8000` (or the port specified in terminal).

### 3. Run Experimental OS Benchmarks
```bash
python benchmark_experiments.py
```
This benchmarks:
- Deadlock Safety sequences under diverse workload vectors
- Mutex vs Semaphore vs Unprotected concurrency throughput
- Scheduling algorithm turnaround times (FCFS vs SJF vs Round Robin vs Priority)

### 4. Run the Integration Test Suite
```bash
python tests/test_saas_integration.py
```

---

## 👥 Authors & Academic Attribution

**Group 7 — Department of Artificial Intelligence, NIET Greater Noida:**
- **Samar Singh** (Roll No: 2501331940042)
- **Ishank Rana**
- **Chhavi Attri**
- **Aditi Singh**
- **Pratyush Agrahari**

**Faculty Mentors:**
- **Mr. Amar Pal Yadav** (Assistant Professor, Department of AI)
- **Dr. Varsha Jotwani** (Associate Professor, Department of AI)

**Course:** Operating Systems (CCSE0303A)  
**UN SDG Alignment:** Goal 11: Sustainable Cities and Communities (Target 11.2 - Sustainable Transport Systems)

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
