"""
Smart Parking Management System - CPU Scheduling Simulation Engine
Unit 2: Process & Thread Management - CPU Scheduling Algorithms
Algorithms Implemented:
  1. FCFS (First-Come, First-Served)
  2. SJF (Shortest Job First - Non-Preemptive)
  3. SRTF (Shortest Remaining Time First - Preemptive)
  4. Priority Non-Preemptive
  5. Priority Preemptive
  6. Round Robin (with dynamic time quantum)
"""

from typing import List, Dict, Any
import copy


class SchedulingEngine:
    @staticmethod
    def _prepare_processes(processes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        clean = []
        for p in processes:
            clean.append({
                "pid": str(p["pid"]),
                "plate": str(p.get("plate", p["pid"])),
                "arrival_time": float(p["arrival_time"]),
                "burst_time": float(p["burst_time"]),
                "priority": int(p.get("priority", 4)),
                "vehicle_type": p.get("vehicle_type", "STANDARD")
            })
        return sorted(clean, key=lambda x: (x["arrival_time"], x["pid"]))

    @classmethod
    def fcfs(cls, processes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """First-Come, First-Served (FCFS) Non-Preemptive Scheduling."""
        procs = cls._prepare_processes(processes)
        if not procs:
            return cls._empty_result("FCFS")

        timeline = []
        current_time = 0.0
        results = {}

        for p in procs:
            if current_time < p["arrival_time"]:
                # CPU / Allocator is idle
                timeline.append({
                    "pid": "IDLE",
                    "start": current_time,
                    "end": p["arrival_time"]
                })
                current_time = p["arrival_time"]

            start_t = current_time
            end_t = current_time + p["burst_time"]
            timeline.append({
                "pid": p["pid"],
                "plate": p["plate"],
                "start": start_t,
                "end": end_t
            })

            ct = end_t
            tat = ct - p["arrival_time"]
            wt = tat - p["burst_time"]
            rt = start_t - p["arrival_time"]

            results[p["pid"]] = {
                "pid": p["pid"],
                "plate": p["plate"],
                "arrival_time": p["arrival_time"],
                "burst_time": p["burst_time"],
                "priority": p["priority"],
                "completion_time": round(ct, 2),
                "turnaround_time": round(tat, 2),
                "waiting_time": round(wt, 2),
                "response_time": round(rt, 2)
            }
            current_time = end_t

        return cls._compile_metrics("FCFS", timeline, results, current_time)

    @classmethod
    def sjf(cls, processes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Shortest Job First (SJF) Non-Preemptive Scheduling."""
        procs = cls._prepare_processes(processes)
        if not procs:
            return cls._empty_result("SJF (Non-Preemptive)")

        timeline = []
        completed = {}
        ready_queue = []
        remaining = copy.deepcopy(procs)
        current_time = 0.0

        while len(completed) < len(procs):
            # Check arrivals
            newly_arrived = [p for p in remaining if p["arrival_time"] <= current_time]
            for p in newly_arrived:
                ready_queue.append(p)
                remaining.remove(p)

            if not ready_queue:
                if remaining:
                    next_arrival = min(p["arrival_time"] for p in remaining)
                    timeline.append({
                        "pid": "IDLE",
                        "start": current_time,
                        "end": next_arrival
                    })
                    current_time = next_arrival
                    continue
                else:
                    break

            # Pick process with minimum burst time
            ready_queue.sort(key=lambda x: (x["burst_time"], x["arrival_time"], x["pid"]))
            chosen = ready_queue.pop(0)

            start_t = current_time
            end_t = current_time + chosen["burst_time"]
            timeline.append({
                "pid": chosen["pid"],
                "plate": chosen["plate"],
                "start": start_t,
                "end": end_t
            })

            ct = end_t
            tat = ct - chosen["arrival_time"]
            wt = tat - chosen["burst_time"]
            rt = start_t - chosen["arrival_time"]

            completed[chosen["pid"]] = {
                "pid": chosen["pid"],
                "plate": chosen["plate"],
                "arrival_time": chosen["arrival_time"],
                "burst_time": chosen["burst_time"],
                "priority": chosen["priority"],
                "completion_time": round(ct, 2),
                "turnaround_time": round(tat, 2),
                "waiting_time": round(wt, 2),
                "response_time": round(rt, 2)
            }
            current_time = end_t

        return cls._compile_metrics("SJF (Non-Preemptive)", timeline, completed, current_time)

    @classmethod
    def srtf(cls, processes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Shortest Remaining Time First (SRTF) Preemptive Scheduling."""
        procs = cls._prepare_processes(processes)
        if not procs:
            return cls._empty_result("SRTF (Preemptive)")

        remaining_procs = {
            p["pid"]: {
                **p,
                "rem_burst": p["burst_time"],
                "first_start": None,
                "completion_time": None
            }
            for p in procs
        }

        timeline = []
        current_time = 0.0
        completed_count = 0
        total_count = len(procs)
        dt = 0.5  # simulation resolution time step

        active_pid = None
        seg_start = None

        while completed_count < total_count:
            # Find eligible processes arrived by current_time with rem_burst > 0
            eligible = [
                p for p in remaining_procs.values()
                if p["arrival_time"] <= current_time and p["rem_burst"] > 0
            ]

            if not eligible:
                # Next arrival jump
                uncompleted = [p for p in remaining_procs.values() if p["rem_burst"] > 0]
                if uncompleted:
                    next_arr = min(p["arrival_time"] for p in uncompleted)
                    if active_pid:
                        timeline.append({
                            "pid": active_pid,
                            "plate": remaining_procs[active_pid]["plate"],
                            "start": seg_start,
                            "end": current_time
                        })
                        active_pid = None

                    timeline.append({
                        "pid": "IDLE",
                        "start": current_time,
                        "end": next_arr
                    })
                    current_time = next_arr
                    continue
                else:
                    break

            # Pick shortest remaining burst
            eligible.sort(key=lambda x: (x["rem_burst"], x["arrival_time"], x["pid"]))
            chosen = eligible[0]

            if chosen["first_start"] is None:
                chosen["first_start"] = current_time

            if chosen["pid"] != active_pid:
                # Context switch
                if active_pid is not None:
                    timeline.append({
                        "pid": active_pid,
                        "plate": remaining_procs[active_pid]["plate"],
                        "start": seg_start,
                        "end": current_time
                    })
                active_pid = chosen["pid"]
                seg_start = current_time

            # Advance by step or till completion
            step = min(dt, chosen["rem_burst"])
            chosen["rem_burst"] -= step
            current_time += step

            if chosen["rem_burst"] <= 0.0001:
                chosen["rem_burst"] = 0
                chosen["completion_time"] = current_time
                completed_count += 1
                timeline.append({
                    "pid": active_pid,
                    "plate": remaining_procs[active_pid]["plate"],
                    "start": seg_start,
                    "end": current_time
                })
                active_pid = None

        # Clean merged timeline segments
        cleaned_timeline = cls._merge_adjacent_segments(timeline)

        results = {}
        for p in remaining_procs.values():
            ct = p["completion_time"]
            tat = ct - p["arrival_time"]
            wt = tat - p["burst_time"]
            rt = p["first_start"] - p["arrival_time"]
            results[p["pid"]] = {
                "pid": p["pid"],
                "plate": p["plate"],
                "arrival_time": p["arrival_time"],
                "burst_time": p["burst_time"],
                "priority": p["priority"],
                "completion_time": round(ct, 2),
                "turnaround_time": round(tat, 2),
                "waiting_time": round(wt, 2),
                "response_time": round(rt, 2)
            }

        return cls._compile_metrics("SRTF (Preemptive)", cleaned_timeline, results, current_time)

    @classmethod
    def priority_np(cls, processes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Non-Preemptive Priority Scheduling (Lower value = higher priority)."""
        procs = cls._prepare_processes(processes)
        if not procs:
            return cls._empty_result("Priority (Non-Preemptive)")

        timeline = []
        completed = {}
        ready_queue = []
        remaining = copy.deepcopy(procs)
        current_time = 0.0

        while len(completed) < len(procs):
            newly_arrived = [p for p in remaining if p["arrival_time"] <= current_time]
            for p in newly_arrived:
                ready_queue.append(p)
                remaining.remove(p)

            if not ready_queue:
                if remaining:
                    next_arr = min(p["arrival_time"] for p in remaining)
                    timeline.append({
                        "pid": "IDLE",
                        "start": current_time,
                        "end": next_arr
                    })
                    current_time = next_arr
                    continue
                else:
                    break

            ready_queue.sort(key=lambda x: (x["priority"], x["arrival_time"], x["pid"]))
            chosen = ready_queue.pop(0)

            start_t = current_time
            end_t = current_time + chosen["burst_time"]
            timeline.append({
                "pid": chosen["pid"],
                "plate": chosen["plate"],
                "start": start_t,
                "end": end_t
            })

            ct = end_t
            tat = ct - chosen["arrival_time"]
            wt = tat - chosen["burst_time"]
            rt = start_t - chosen["arrival_time"]

            completed[chosen["pid"]] = {
                "pid": chosen["pid"],
                "plate": chosen["plate"],
                "arrival_time": chosen["arrival_time"],
                "burst_time": chosen["burst_time"],
                "priority": chosen["priority"],
                "completion_time": round(ct, 2),
                "turnaround_time": round(tat, 2),
                "waiting_time": round(wt, 2),
                "response_time": round(rt, 2)
            }
            current_time = end_t

        return cls._compile_metrics("Priority (Non-Preemptive)", timeline, completed, current_time)

    @classmethod
    def priority_p(cls, processes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Preemptive Priority Scheduling (Emergency vehicles preempt standard)."""
        procs = cls._prepare_processes(processes)
        if not procs:
            return cls._empty_result("Priority (Preemptive)")

        remaining_procs = {
            p["pid"]: {
                **p,
                "rem_burst": p["burst_time"],
                "first_start": None,
                "completion_time": None
            }
            for p in procs
        }

        timeline = []
        current_time = 0.0
        completed_count = 0
        total_count = len(procs)
        dt = 0.5

        active_pid = None
        seg_start = None

        while completed_count < total_count:
            eligible = [
                p for p in remaining_procs.values()
                if p["arrival_time"] <= current_time and p["rem_burst"] > 0
            ]

            if not eligible:
                uncompleted = [p for p in remaining_procs.values() if p["rem_burst"] > 0]
                if uncompleted:
                    next_arr = min(p["arrival_time"] for p in uncompleted)
                    if active_pid:
                        timeline.append({
                            "pid": active_pid,
                            "plate": remaining_procs[active_pid]["plate"],
                            "start": seg_start,
                            "end": current_time
                        })
                        active_pid = None

                    timeline.append({
                        "pid": "IDLE",
                        "start": current_time,
                        "end": next_arr
                    })
                    current_time = next_arr
                    continue
                else:
                    break

            eligible.sort(key=lambda x: (x["priority"], x["arrival_time"], x["pid"]))
            chosen = eligible[0]

            if chosen["first_start"] is None:
                chosen["first_start"] = current_time

            if chosen["pid"] != active_pid:
                if active_pid is not None:
                    timeline.append({
                        "pid": active_pid,
                        "plate": remaining_procs[active_pid]["plate"],
                        "start": seg_start,
                        "end": current_time
                    })
                active_pid = chosen["pid"]
                seg_start = current_time

            step = min(dt, chosen["rem_burst"])
            chosen["rem_burst"] -= step
            current_time += step

            if chosen["rem_burst"] <= 0.0001:
                chosen["rem_burst"] = 0
                chosen["completion_time"] = current_time
                completed_count += 1
                timeline.append({
                    "pid": active_pid,
                    "plate": remaining_procs[active_pid]["plate"],
                    "start": seg_start,
                    "end": current_time
                })
                active_pid = None

        cleaned_timeline = cls._merge_adjacent_segments(timeline)

        results = {}
        for p in remaining_procs.values():
            ct = p["completion_time"]
            tat = ct - p["arrival_time"]
            wt = tat - p["burst_time"]
            rt = p["first_start"] - p["arrival_time"]
            results[p["pid"]] = {
                "pid": p["pid"],
                "plate": p["plate"],
                "arrival_time": p["arrival_time"],
                "burst_time": p["burst_time"],
                "priority": p["priority"],
                "completion_time": round(ct, 2),
                "turnaround_time": round(tat, 2),
                "waiting_time": round(wt, 2),
                "response_time": round(rt, 2)
            }

        return cls._compile_metrics("Priority (Preemptive)", cleaned_timeline, results, current_time)

    @classmethod
    def round_robin(cls, processes: List[Dict[str, Any]], quantum: float = 2.0) -> Dict[str, Any]:
        """Round Robin (RR) Scheduling with Configurable Time Quantum."""
        procs = cls._prepare_processes(processes)
        if not procs:
            return cls._empty_result(f"Round Robin (q={quantum})")

        remaining_procs = {
            p["pid"]: {
                **p,
                "rem_burst": p["burst_time"],
                "first_start": None,
                "completion_time": None
            }
            for p in procs
        }

        timeline = []
        ready_queue = []
        completed = {}
        current_time = 0.0
        arrivals = copy.deepcopy(procs)

        # Initial arrival check
        while arrivals and arrivals[0]["arrival_time"] <= current_time:
            p = arrivals.pop(0)
            ready_queue.append(p["pid"])

        while len(completed) < len(procs):
            if not ready_queue:
                if arrivals:
                    next_arr = arrivals[0]["arrival_time"]
                    timeline.append({
                        "pid": "IDLE",
                        "start": current_time,
                        "end": next_arr
                    })
                    current_time = next_arr
                    while arrivals and arrivals[0]["arrival_time"] <= current_time:
                        p = arrivals.pop(0)
                        ready_queue.append(p["pid"])
                    continue
                else:
                    break

            curr_pid = ready_queue.pop(0)
            p_data = remaining_procs[curr_pid]

            if p_data["first_start"] is None:
                p_data["first_start"] = current_time

            exec_time = min(quantum, p_data["rem_burst"])
            start_t = current_time
            end_t = current_time + exec_time

            timeline.append({
                "pid": curr_pid,
                "plate": p_data["plate"],
                "start": start_t,
                "end": end_t
            })

            p_data["rem_burst"] -= exec_time
            current_time = end_t

            # Enqueue any new arrivals during this execution window
            while arrivals and arrivals[0]["arrival_time"] <= current_time:
                arrived = arrivals.pop(0)
                ready_queue.append(arrived["pid"])

            if p_data["rem_burst"] <= 0.0001:
                p_data["rem_burst"] = 0
                p_data["completion_time"] = current_time
                completed[curr_pid] = True
            else:
                ready_queue.append(curr_pid)

        cleaned_timeline = cls._merge_adjacent_segments(timeline)

        results = {}
        for p in remaining_procs.values():
            ct = p["completion_time"]
            tat = ct - p["arrival_time"]
            wt = tat - p["burst_time"]
            rt = p["first_start"] - p["arrival_time"]
            results[p["pid"]] = {
                "pid": p["pid"],
                "plate": p["plate"],
                "arrival_time": p["arrival_time"],
                "burst_time": p["burst_time"],
                "priority": p["priority"],
                "completion_time": round(ct, 2),
                "turnaround_time": round(tat, 2),
                "waiting_time": round(wt, 2),
                "response_time": round(rt, 2)
            }

        return cls._compile_metrics(f"Round Robin (q={quantum})", cleaned_timeline, results, current_time)

    @classmethod
    def compare_all(cls, processes: List[Dict[str, Any]], quantum: float = 2.0) -> Dict[str, Any]:
        """Runs all 6 algorithms on the same input dataset and provides comparative analysis."""
        return {
            "fcfs": cls.fcfs(processes),
            "sjf": cls.sjf(processes),
            "srtf": cls.srtf(processes),
            "priority_np": cls.priority_np(processes),
            "priority_p": cls.priority_p(processes),
            "round_robin": cls.round_robin(processes, quantum)
        }

    @staticmethod
    def _merge_adjacent_segments(timeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not timeline:
            return []
        merged = [timeline[0]]
        for seg in timeline[1:]:
            prev = merged[-1]
            if prev["pid"] == seg["pid"] and abs(prev["end"] - seg["start"]) < 0.001:
                prev["end"] = seg["end"]
            else:
                merged.append(seg)
        return merged

    @staticmethod
    def _compile_metrics(
        algo_name: str,
        timeline: List[Dict[str, Any]],
        results: Dict[str, Any],
        total_time: float
    ) -> Dict[str, Any]:
        procs = list(results.values())
        count = len(procs)
        if count == 0 or total_time == 0:
            return {
                "algorithm": algo_name,
                "timeline": timeline,
                "processes": results,
                "metrics": {
                    "avg_waiting_time": 0.0,
                    "avg_turnaround_time": 0.0,
                    "avg_response_time": 0.0,
                    "total_time": 0.0,
                    "cpu_utilization": 0.0,
                    "throughput": 0.0
                }
            }

        avg_wt = sum(p["waiting_time"] for p in procs) / count
        avg_tat = sum(p["turnaround_time"] for p in procs) / count
        avg_rt = sum(p["response_time"] for p in procs) / count
        busy_time = sum(seg["end"] - seg["start"] for seg in timeline if seg["pid"] != "IDLE")
        utilization = (busy_time / total_time * 100.0) if total_time > 0 else 0.0
        throughput = (count / total_time) if total_time > 0 else 0.0

        return {
            "algorithm": algo_name,
            "timeline": timeline,
            "processes": results,
            "metrics": {
                "avg_waiting_time": round(avg_wt, 2),
                "avg_turnaround_time": round(avg_tat, 2),
                "avg_response_time": round(avg_rt, 2),
                "total_time": round(total_time, 2),
                "cpu_utilization": round(utilization, 2),
                "throughput": round(throughput, 4)
            }
        }

    @staticmethod
    def _empty_result(algo_name: str) -> Dict[str, Any]:
        return {
            "algorithm": algo_name,
            "timeline": [],
            "processes": {},
            "metrics": {
                "avg_waiting_time": 0.0,
                "avg_turnaround_time": 0.0,
                "avg_response_time": 0.0,
                "total_time": 0.0,
                "cpu_utilization": 0.0,
                "throughput": 0.0
            }
        }
