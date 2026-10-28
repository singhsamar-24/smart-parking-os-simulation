# -*- coding: utf-8 -*-
"""
Smart Parking Management System - Banker's Algorithm (Deadlock Avoidance)
Unit 3: Concurrency and Deadlock Management

Implements:
  1. Safety Algorithm - finds a safe execution order (or reports deadlock risk)
  2. Resource Request - checks if a new slot request can be safely granted
  3. RAG Cycle Detection - detects circular waits in a Resource Allocation Graph
"""

from typing import List, Dict, Any, Tuple, Optional
import copy


class BankersAlgorithmEngine:
    # Human-readable names for the 4 parking resource types
    RESOURCE_NAMES = ["Compact Slot", "EV Charging", "SUV Bay", "Valet Bay"]

    def __init__(self):
        # Default state: 5 vehicle processes, 4 resource types
        self.num_processes = 5
        self.num_resources = 4

        # How many of each resource slot are currently free
        self.available = [3, 3, 2, 2]

        # Maximum resources each vehicle process could ever need
        self.max_matrix = [
            [7, 5, 3, 2],   # P0 - Fleet Van
            [3, 2, 2, 2],   # P1 - EV Taxi
            [9, 0, 2, 2],   # P2 - Heavy Truck
            [2, 2, 2, 1],   # P3 - Compact EV
            [4, 3, 3, 2],   # P4 - Family SUV
        ]

        # Resources already allocated to each vehicle process
        self.allocation_matrix = [
            [0, 1, 0, 0],   # P0
            [2, 0, 0, 1],   # P1
            [3, 0, 2, 1],   # P2
            [2, 1, 1, 0],   # P3
            [0, 0, 2, 0],   # P4
        ]

        self.process_names = [
            "P0 (Fleet Van)",
            "P1 (EV Taxi)",
            "P2 (Heavy Truck)",
            "P3 (Compact EV)",
            "P4 (Family SUV)",
        ]

    # Helpers
    def _need_matrix(self, alloc: List[List[int]], max_mat: List[List[int]]) -> List[List[int]]:
        """Need[i][j] = Max[i][j] - Allocation[i][j] (cannot go below 0)."""
        return [
            [max(0, max_mat[i][j] - alloc[i][j]) for j in range(len(alloc[i]))]
            for i in range(len(alloc))
        ]

    @staticmethod
    def _fits(request: List[int], available: List[int]) -> bool:
        """True when every element of request <= corresponding available slot."""
        return all(r <= a for r, a in zip(request, available))

    # 1. Safety Algorithm
    def run_safety_algorithm(
        self,
        available:  Optional[List[int]]       = None,
        allocation: Optional[List[List[int]]] = None,
        max_mat:    Optional[List[List[int]]] = None,
    ) -> Dict[str, Any]:
        """
        Banker's Safety Algorithm:
        Work = copy of Available vector
        Finish[i] = False for all i

        Repeat until no progress:
            Find any process i where Finish[i]=False AND Need[i] <= Work
            -> simulate it finishing: Work += Allocation[i], Finish[i] = True

        If all Finish[i] = True -> SAFE (return safe sequence)
        Else                    -> UNSAFE (deadlock risk)
        """
        avail  = list(available  if available  is not None else self.available)
        alloc  = copy.deepcopy(allocation if allocation is not None else self.allocation_matrix)
        maxmat = copy.deepcopy(max_mat    if max_mat    is not None else self.max_matrix)
        need   = self._need_matrix(alloc, maxmat)

        n      = len(alloc)
        work   = list(avail)
        finish = [False] * n
        safe_sequence: List[str] = []
        steps: List[Dict[str, Any]] = []

        # Main loop - keep scanning until no process can be added
        while True:
            found = False
            for i in range(n):
                if finish[i]:
                    continue
                p_name = self.process_names[i] if i < len(self.process_names) else f"P{i}"

                if self._fits(need[i], work):
                    work_before = list(work)
                    work = [work[j] + alloc[i][j] for j in range(len(work))]
                    finish[i] = True
                    safe_sequence.append(f"P{i}")
                    found = True

                    steps.append({
                        "process":       f"P{i}",
                        "name":          p_name,
                        "need":          need[i],
                        "work_before":   work_before,
                        "condition_met": True,
                        "action":        (
                            f"Need {need[i]} <= Work {work_before} [OK] -> "
                            f"P{i} can finish. Release allocation {alloc[i]}. "
                            f"Work becomes {work}."
                        ),
                        "work_after": list(work),
                    })
                else:
                    steps.append({
                        "process":       f"P{i}",
                        "name":          p_name,
                        "need":          need[i],
                        "work_before":   list(work),
                        "condition_met": False,
                        "action":        (
                            f"Need {need[i]} > Work {work} [WAIT] -> "
                            f"P{i} must wait (not enough free slots)."
                        ),
                        "work_after": list(work),
                    })
            if not found:
                break

        is_safe = all(finish)
        return {
            "is_safe":              is_safe,
            "safe_sequence":        safe_sequence if is_safe else [],
            "safe_sequence_string": " -> ".join(safe_sequence) if is_safe
                                    else "No safe sequence - Deadlock Risk!",
            "finish_vector":        finish,
            "final_work":           work,
            "trace_steps":          steps,
            "matrices": {
                "available":      avail,
                "allocation":     alloc,
                "max":            maxmat,
                "need":           need,
                "resource_names": self.RESOURCE_NAMES,
                "process_names":  self.process_names,
            },
        }

    # 2. Resource Request
    def request_resources(
        self,
        process_idx: int,
        request:     List[int],
    ) -> Dict[str, Any]:
        """
        Banker's Resource Request Algorithm:
        Step 1: Check Request <= Need
        Step 2: Check Request <= Available
        Step 3: Tentatively allocate resources
        Step 4: Run safety algorithm on tentative state
                If safe   -> grant request
                If unsafe -> revert allocation and deny
        """
        p = process_idx
        steps: List[str] = []

        if p < 0 or p >= self.num_processes:
            return {"granted": False, "reason": f"Invalid process index P{p}."}

        need = self._need_matrix(self.allocation_matrix, self.max_matrix)

        # Step 1: Request <= Need
        if not self._fits(request, need[p]):
            msg = (
                f"Step 1 Error: Process P{p} requested {request}, "
                f"which exceeds its declared Need {need[p]}."
            )
            return {
                "granted":       False,
                "reason":        msg,
                "step_failed":   1,
                "safe_sequence": [],
                "steps":         [msg],
            }
        steps.append(f"Step 1 OK: Request {request} <= Need {need[p]}.")

        # Step 2: Request <= Available
        if not self._fits(request, self.available):
            msg = (
                f"Step 2 Wait: Request {request} exceeds currently "
                f"Available slots {self.available}. Process P{p} must wait."
            )
            return {
                "granted":       False,
                "reason":        msg,
                "step_failed":   2,
                "safe_sequence": [],
                "steps":         steps + [msg],
            }
        steps.append(f"Step 2 OK: Request {request} <= Available {self.available}.")

        # Step 3: Tentative Allocation
        t_avail = [self.available[j] - request[j] for j in range(self.num_resources)]
        t_alloc = copy.deepcopy(self.allocation_matrix)
        t_alloc[p] = [t_alloc[p][j] + request[j] for j in range(self.num_resources)]
        steps.append(
            f"Step 3 Tentative: Tentatively allocated. New Available = {t_avail}."
        )

        # Step 4: Safety Check on tentative state
        safety = self.run_safety_algorithm(
            available=t_avail,
            allocation=t_alloc,
            max_mat=self.max_matrix,
        )

        if safety["is_safe"]:
            self.available         = t_avail
            self.allocation_matrix = t_alloc
            steps.append(
                f"Step 4 OK: System remains SAFE. Sequence: {safety['safe_sequence_string']}"
            )
            return {
                "granted":        True,
                "message":        f"Request GRANTED for P{p}! System stays safe.",
                "safe_sequence":  safety["safe_sequence"],
                "steps":          steps,
                "new_available":  t_avail,
                "new_allocation": t_alloc,
            }
        else:
            steps.append("Step 4 Wait: Tentative state is UNSAFE. Reverting. Request denied.")
            return {
                "granted":       False,
                "reason":        "Granting this request would cause a potential Deadlock. Denied.",
                "step_failed":   4,
                "safe_sequence": [],
                "steps":         steps,
            }

    # 3. RAG Cycle Detection
    def detect_rag_deadlock(
        self,
        nodes: List[str],
        edges: List[Tuple[str, str]],
    ) -> Dict[str, Any]:
        """
        Build a Resource Allocation Graph and detect cycles using DFS.
        A cycle in a single-instance RAG means Deadlock.
        """
        adj: Dict[str, List[str]] = {n: [] for n in nodes}
        for u, v in edges:
            if u in adj:
                adj[u].append(v)

        colour = {n: 0 for n in nodes}   # 0=white, 1=grey, 2=black
        cycles: List[List[str]] = []

        def dfs(node: str, path: List[str]):
            colour[node] = 1
            path.append(node)
            for neighbour in adj.get(node, []):
                if colour[neighbour] == 1:
                    idx = path.index(neighbour)
                    cycles.append(path[idx:] + [neighbour])
                elif colour[neighbour] == 0:
                    dfs(neighbour, path)
            path.pop()
            colour[node] = 2

        for node in nodes:
            if colour[node] == 0:
                dfs(node, [])

        deadlock = len(cycles) > 0
        cycle_str = " -> ".join(cycles[0]) if cycles else "None (no circular wait)"
        return {
            "deadlock":             deadlock,
            "deadlock_detected":    deadlock,
            "cycles":               cycles,
            "cycle_summary":        cycle_str,
            "coffman_conditions": {
                "mutual_exclusion": "Active - one vehicle per bay",
                "hold_and_wait":    "Active - holds ramp, waits for bay",
                "no_preemption":    "Active - cannot force a vehicle out",
                "circular_wait":    "PRESENT - cycle detected!" if deadlock
                                    else "Absent - graph is acyclic",
            },
            "recovery_recommendation":
                "Preempt the lowest-priority vehicle to break the cycle."
                if deadlock else "System running smoothly - no deadlock.",
        }
