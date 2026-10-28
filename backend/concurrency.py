"""
Smart Parking Management System - Concurrency & Synchronization Module
Unit 3: Concurrency and Deadlock Management
Implements:
  1. Race Condition Simulator (Unsynchronized vs Mutex-Synchronized Slot Allocation)
  2. Peterson's Solution Simulator (Software Mutual Exclusion for 2 Processes)
  3. Test-and-Set Lock (Hardware Atomic Instruction Simulation)
  4. Counting Semaphore (Slot Resource Counting & Queuing)
"""

import threading
import time
from typing import Dict, Any, List, Optional


class ConcurrencyLab:
    def __init__(self):
        # Simulated Hardware & OS Locks
        self.system_mutex = threading.Lock()
        self.slot_locks: Dict[str, threading.Lock] = {}
        
        # Peterson's Algorithm Shared State for P0 and P1
        self.peterson_flags = [False, False]
        self.peterson_turn = 0
        self.peterson_history = []
        
        # Test-and-Set Lock Atomic Variable
        self.tsl_lock = False
        self.tsl_history = []
        
        # Counting Semaphore for Available Parking Slots (Capacity = 16)
        self.counting_semaphore_capacity = 16
        self.counting_semaphore_value = 16
        self.semaphore_blocked_queue: List[str] = []

    def simulate_race_condition(self, slot_id: str = "S05", vehicle_a: str = "Car-A (P101)", vehicle_b: str = "Car-B (P102)") -> Dict[str, Any]:
        """
        Simulates two threads attempting to allocate the same parking slot simultaneously
        WITHOUT synchronization, creating a race condition and critical section violation.
        """
        trace = []
        slot_state = {"slot_id": slot_id, "status": "FREE", "allocated_to": None, "collision": False}

        trace.append({
            "step": 1,
            "thread": "Thread A (" + vehicle_a + ")",
            "action": f"Checks status of {slot_id}",
            "slot_status": slot_state["status"],
            "detail": f"Thread A observes {slot_id} is FREE."
        })
        
        trace.append({
            "step": 2,
            "thread": "Thread B (" + vehicle_b + ")",
            "action": f"Checks status of {slot_id} [Interleaved Before A updates!]",
            "slot_status": slot_state["status"],
            "detail": f"Thread B also observes {slot_id} is FREE due to lack of lock (Race Condition!)."
        })

        trace.append({
            "step": 3,
            "thread": "Thread A (" + vehicle_a + ")",
            "action": f"Writes allocated_to = '{vehicle_a}'",
            "slot_status": "OCCUPIED",
            "detail": f"Thread A completes write and assumes exclusive ownership of {slot_id}."
        })
        slot_state["allocated_to"] = vehicle_a
        slot_state["status"] = "OCCUPIED"

        trace.append({
            "step": 4,
            "thread": "Thread B (" + vehicle_b + ")",
            "action": f"Overwrites allocated_to = '{vehicle_b}' [Collision!]",
            "slot_status": "CORRUPTED / DOUBLE_BOOKED",
            "detail": f"Thread B overwrites {slot_id}! Both vehicles attempt to park in the same slot simultaneously."
        })
        slot_state["status"] = "CORRUPTED_COLLISION"
        slot_state["collision"] = True
        slot_state["allocated_to"] = f"{vehicle_a} & {vehicle_b}"

        return {
            "mode": "UNSYNCHRONIZED_RACE_CONDITION",
            "slot_id": slot_id,
            "trace": trace,
            "final_slot_state": slot_state,
            "critical_section_violated": True,
            "hazard": "RACE CONDITION DETECTED: Mutual exclusion breached! Two processes entered critical section simultaneously."
        }

    def simulate_synchronized_allocation(self, slot_id: str = "S05", vehicle_a: str = "Car-A (P101)", vehicle_b: str = "Car-B (P102)") -> Dict[str, Any]:
        """
        Simulates two threads attempting to allocate the same parking slot
        WITH a Mutex Lock protecting the Critical Section.
        """
        trace = []
        slot_state = {"slot_id": slot_id, "status": "FREE", "allocated_to": None, "lock_holder": None}

        trace.append({
            "step": 1,
            "thread": "Thread A (" + vehicle_a + ")",
            "action": f"Entry Section: mutex.acquire({slot_id})",
            "lock_state": "LOCKED by Thread A",
            "detail": f"Thread A successfully acquires Mutex lock for {slot_id}."
        })
        slot_state["lock_holder"] = vehicle_a

        trace.append({
            "step": 2,
            "thread": "Thread B (" + vehicle_b + ")",
            "action": f"Entry Section: mutex.acquire({slot_id})",
            "lock_state": "BLOCKED (Waiting for lock)",
            "detail": f"Thread B is BLOCKED and placed in the wait queue because Mutex is held by Thread A."
        })

        trace.append({
            "step": 3,
            "thread": "Thread A (" + vehicle_a + ")",
            "action": f"Critical Section: Verify & Allocate {slot_id}",
            "lock_state": "LOCKED by Thread A",
            "detail": f"Inside Critical Section: Thread A finds {slot_id} FREE and safely sets occupant = {vehicle_a}."
        })
        slot_state["status"] = "OCCUPIED"
        slot_state["allocated_to"] = vehicle_a

        trace.append({
            "step": 4,
            "thread": "Thread A (" + vehicle_a + ")",
            "action": f"Exit Section: mutex.release({slot_id})",
            "lock_state": "UNLOCKED / Signal next",
            "detail": f"Thread A completes critical section, releases Mutex, and wakes up blocked Thread B."
        })
        slot_state["lock_holder"] = None

        trace.append({
            "step": 5,
            "thread": "Thread B (" + vehicle_b + ")",
            "action": f"Critical Section: Wakes up, re-checks {slot_id}",
            "lock_state": "LOCKED by Thread B",
            "detail": f"Thread B acquires lock, verifies {slot_id} is already OCCUPIED by {vehicle_a}, and gracefully redirects to next free slot (e.g. S06)."
        })
        slot_state["alternate_slot_allocated_to_b"] = "S06"

        return {
            "mode": "SYNCHRONIZED_MUTEX",
            "slot_id": slot_id,
            "trace": trace,
            "final_slot_state": slot_state,
            "critical_section_violated": False,
            "protection": "SAFE CONCURRENCY: Mutual exclusion maintained! Critical section protected by Mutex lock."
        }

    def trace_petersons_algorithm(self) -> Dict[str, Any]:
        """
        Step-by-step trace of Peterson's Solution for 2 processes competing for entry gate access.
        Satisfies: Mutual Exclusion, Progress, and Bounded Waiting.
        """
        steps = [
            {
                "step": 1,
                "process": "P0 (North Gate)",
                "code": "flag[0] = True; turn = 1;",
                "flag_0": True,
                "flag_1": False,
                "turn": 1,
                "explanation": "P0 declares desire to enter critical section, but politely yields turn to P1."
            },
            {
                "step": 2,
                "process": "P1 (South Gate)",
                "code": "flag[1] = True; turn = 0;",
                "flag_0": True,
                "flag_1": True,
                "turn": 0,
                "explanation": "P1 declares desire to enter critical section, and sets turn to 0."
            },
            {
                "step": 3,
                "process": "P0 (North Gate)",
                "code": "while (flag[1] && turn == 1) /* wait */",
                "flag_0": True,
                "flag_1": True,
                "turn": 0,
                "explanation": "P0 checks condition: flag[1] is True, but turn is 0 (not 1). Loop condition evaluates to FALSE! P0 enters Critical Section!"
            },
            {
                "step": 4,
                "process": "P0 (North Gate)",
                "code": "/* CRITICAL SECTION: Allocate Slot S01 */",
                "flag_0": True,
                "flag_1": True,
                "turn": 0,
                "explanation": "P0 safely operates inside Critical Section. Slot S01 allocated to vehicle."
            },
            {
                "step": 5,
                "process": "P1 (South Gate)",
                "code": "while (flag[0] && turn == 0) /* wait */",
                "flag_0": True,
                "flag_1": True,
                "turn": 0,
                "explanation": "P1 checks condition: flag[0] is True AND turn is 0. Condition is TRUE! P1 correctly waits in Entry Section."
            },
            {
                "step": 6,
                "process": "P0 (North Gate)",
                "code": "/* EXIT SECTION */ flag[0] = False;",
                "flag_0": False,
                "flag_1": True,
                "turn": 0,
                "explanation": "P0 exits Critical Section, clears flag[0] = False. P1's while loop condition becomes FALSE immediately."
            },
            {
                "step": 7,
                "process": "P1 (South Gate)",
                "code": "/* CRITICAL SECTION: Allocate Slot S02 */",
                "flag_0": False,
                "flag_1": True,
                "turn": 0,
                "explanation": "P1 enters Critical Section and safely allocates Slot S02. Mutual Exclusion, Progress, and Bounded Waiting guaranteed!"
            }
        ]
        return {
            "title": "Peterson's Algorithm Mutual Exclusion Verification",
            "properties_satisfied": {
                "mutual_exclusion": "Proven - Both processes cannot be in critical section simultaneously.",
                "progress": "Proven - Selection of process entering is not delayed indefinitely.",
                "bounded_waiting": "Proven - Bound on turns exists; process waiting is guaranteed entry next turn."
            },
            "steps": steps
        }

    def trace_test_and_set(self) -> Dict[str, Any]:
        """
        Hardware Test-and-Set Lock (TSL) simulation.
        Atomic hardware primitive: returns old value and sets lock to True in one atomic machine cycle.
        """
        steps = [
            {
                "step": 1,
                "hardware_state": "Lock = 0 (FREE)",
                "process": "P0",
                "instruction": "TestAndSet(&lock)",
                "old_val": 0,
                "new_lock_val": 1,
                "result": "Returns 0 (Lock acquired). P0 enters Critical Section."
            },
            {
                "step": 2,
                "hardware_state": "Lock = 1 (LOCKED)",
                "process": "P1",
                "instruction": "TestAndSet(&lock) [Spinlock]",
                "old_val": 1,
                "new_lock_val": 1,
                "result": "Returns 1. Loop continues (Busy Waiting / Spinlock)."
            },
            {
                "step": 3,
                "hardware_state": "Lock = 1 (LOCKED)",
                "process": "P0",
                "instruction": "lock = 0 /* Release in Exit Section */",
                "old_val": 1,
                "new_lock_val": 0,
                "result": "P0 resets lock to 0 upon departing slot allocation."
            },
            {
                "step": 4,
                "hardware_state": "Lock = 0 (FREE)",
                "process": "P1",
                "instruction": "TestAndSet(&lock)",
                "old_val": 0,
                "new_lock_val": 1,
                "result": "Returns 0. Spinlock exits! P1 enters Critical Section safely."
            }
        ]
        return {
            "title": "Hardware Atomic Test-and-Set Lock (TSL) Simulation",
            "concept": "Atomic instruction executed in a single memory cycle to prevent race conditions at kernel level.",
            "steps": steps
        }

    def counting_semaphore_action(self, action: str, pid: str) -> Dict[str, Any]:
        """
        Simulates Counting Semaphore wait (down/P) and signal (up/V) operations.
        Semaphore value represents free parking slots count.
        """
        with self.system_mutex:
            if action == "WAIT":
                self.counting_semaphore_value -= 1
                if self.counting_semaphore_value < 0:
                    self.semaphore_blocked_queue.append(pid)
                    status = "BLOCKED_WAITING"
                    msg = f"No free slot! Semaphore value = {self.counting_semaphore_value}. Process {pid} placed in semaphore wait queue."
                else:
                    status = "GRANTED"
                    msg = f"Slot available! Semaphore decremented to {self.counting_semaphore_value}. Process {pid} enters parking lot."
            elif action == "SIGNAL":
                self.counting_semaphore_value += 1
                unblocked_pid = None
                if self.semaphore_blocked_queue:
                    unblocked_pid = self.semaphore_blocked_queue.pop(0)
                status = "SIGNALED"
                msg = f"Slot released! Semaphore incremented to {self.counting_semaphore_value}."
                if unblocked_pid:
                    msg += f" Process {unblocked_pid} unblocked and granted slot!"
            else:
                status = "QUERY"
                msg = f"Current Semaphore Value = {self.counting_semaphore_value}"

            return {
                "semaphore_value": self.counting_semaphore_value,
                "capacity": self.counting_semaphore_capacity,
                "blocked_queue": list(self.semaphore_blocked_queue),
                "status": status,
                "message": msg
            }
