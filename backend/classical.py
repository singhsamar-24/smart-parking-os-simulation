"""
Smart Parking Management System - Classical Synchronization Problems
Unit 3: Concurrency and Deadlock Management
Implements real-time simulations of:
  1. Producer-Consumer (Bounded Buffer - Gate Ingress & Allocator)
  2. Reader-Writer (Live Digital Availability Signage vs Gate Writes)
  3. Sleeping Barber (Smart Barrier Attendant & Waiting Bays)
  4. Dining Philosophers (Roundabout Intersection Deadlock & Resolution)
"""

import threading
import time
from typing import Dict, Any, List


class ClassicalSyncLab:
    def __init__(self):
        self._lock = threading.Lock()
        
        # 1. Producer-Consumer (Bounded Buffer)
        self.buffer_capacity = 5
        self.buffer_queue: List[str] = ["Car-01", "Car-02"]
        self.pc_mutex = threading.Lock()
        self.pc_history: List[Dict[str, Any]] = []

        # 2. Reader-Writer
        self.read_count = 0
        self.active_readers: List[str] = ["Signboard-North", "Mobile-App-User1"]
        self.active_writer: str = None
        self.rw_slot_count = 14
        self.rw_history: List[Dict[str, Any]] = []

        # 3. Sleeping Barber (Smart Gatekeeper)
        self.gatekeeper_state = "SLEEPING"  # SLEEPING, SERVICING, IDLE
        self.waiting_chairs_capacity = 4
        self.waiting_chairs: List[str] = []
        self.currently_servicing: str = None
        self.barber_history: List[Dict[str, Any]] = []

        # 4. Dining Philosophers (5-way Roundabout)
        # 5 vehicles and 5 road segments
        self.philosopher_states = ["THINKING"] * 5  # THINKING, HUNGRY(WAITING), EATING(CROSSING)
        self.forks_held = [None] * 5  # fork[i] held by which car
        self.dp_history: List[Dict[str, Any]] = []

    # --- PRODUCER-CONSUMER METHODS ---
    def produce_vehicle(self, vehicle_id: str) -> Dict[str, Any]:
        """Producer (Entry Camera) adds vehicle to bounded waiting buffer."""
        with self.pc_mutex:
            if len(self.buffer_queue) >= self.buffer_capacity:
                res = {
                    "success": False,
                    "action": "PRODUCE_BLOCKED",
                    "vehicle": vehicle_id,
                    "buffer": list(self.buffer_queue),
                    "message": f"BUFFER FULL ({len(self.buffer_queue)}/{self.buffer_capacity})! Producer waits on 'empty' semaphore."
                }
            else:
                self.buffer_queue.append(vehicle_id)
                res = {
                    "success": True,
                    "action": "PRODUCED",
                    "vehicle": vehicle_id,
                    "buffer": list(self.buffer_queue),
                    "message": f"Vehicle {vehicle_id} produced into buffer queue ({len(self.buffer_queue)}/{self.buffer_capacity}). Signaled 'full' semaphore."
                }
            self.pc_history.append(res)
            return res

    def consume_vehicle(self) -> Dict[str, Any]:
        """Consumer (Slot Allocator) dispatches vehicle from buffer into parking lot."""
        with self.pc_mutex:
            if not self.buffer_queue:
                res = {
                    "success": False,
                    "action": "CONSUME_BLOCKED",
                    "buffer": [],
                    "message": "BUFFER EMPTY (0/5)! Consumer waits on 'full' semaphore."
                }
            else:
                v = self.buffer_queue.pop(0)
                res = {
                    "success": True,
                    "action": "CONSUMED",
                    "vehicle": v,
                    "buffer": list(self.buffer_queue),
                    "message": f"Vehicle {v} consumed from buffer and dispatched to slot. Signaled 'empty' semaphore."
                }
            self.pc_history.append(res)
            return res

    # --- READER-WRITER METHODS ---
    def start_read(self, reader_id: str) -> Dict[str, Any]:
        """Multiple readers can read slot count concurrently if no writer is active."""
        with self._lock:
            if self.active_writer is not None:
                return {
                    "success": False,
                    "action": "READ_BLOCKED",
                    "reader": reader_id,
                    "message": f"BLOCKED: Writer '{self.active_writer}' holds exclusive write lock (wrt semaphore). Reader must wait."
                }
            self.read_count += 1
            if reader_id not in self.active_readers:
                self.active_readers.append(reader_id)
            return {
                "success": True,
                "action": "READ_STARTED",
                "reader": reader_id,
                "read_count": self.read_count,
                "active_readers": list(self.active_readers),
                "data_observed": f"{self.rw_slot_count} Free Slots",
                "message": f"Reader {reader_id} granted concurrent read access. Total concurrent readers: {self.read_count}."
            }

    def stop_read(self, reader_id: str) -> Dict[str, Any]:
        with self._lock:
            if reader_id in self.active_readers:
                self.active_readers.remove(reader_id)
                self.read_count = max(0, self.read_count - 1)
            return {
                "success": True,
                "action": "READ_STOPPED",
                "reader": reader_id,
                "read_count": self.read_count,
                "active_readers": list(self.active_readers),
                "message": f"Reader {reader_id} finished reading."
            }

    def start_write(self, writer_id: str, new_slot_count: int) -> Dict[str, Any]:
        """Writer requires exclusive access: no readers and no other writers."""
        with self._lock:
            if self.read_count > 0 or self.active_writer is not None:
                return {
                    "success": False,
                    "action": "WRITE_BLOCKED",
                    "writer": writer_id,
                    "reason": f"Conflict: {self.read_count} active reader(s) or writer '{self.active_writer}' holds wrt lock.",
                    "message": f"Writer {writer_id} BLOCKED waiting for wrt lock."
                }
            self.active_writer = writer_id
            self.rw_slot_count = new_slot_count
            return {
                "success": True,
                "action": "WRITE_STARTED",
                "writer": writer_id,
                "new_data": f"{new_slot_count} Free Slots",
                "message": f"Writer {writer_id} acquired exclusive wrt lock. All other readers and writers locked out."
            }

    def stop_write(self) -> Dict[str, Any]:
        with self._lock:
            old_writer = self.active_writer
            self.active_writer = None
            return {
                "success": True,
                "action": "WRITE_RELEASED",
                "previous_writer": old_writer,
                "message": f"Writer {old_writer} updated database and released wrt lock. Waiting readers may now proceed."
            }

    # --- SLEEPING BARBER METHODS ---
    def arrive_at_gate(self, car_id: str) -> Dict[str, Any]:
        """Vehicle arrives at gatekeeper booth."""
        with self._lock:
            if self.gatekeeper_state == "SLEEPING":
                self.gatekeeper_state = "SERVICING"
                self.currently_servicing = car_id
                return {
                    "success": True,
                    "action": "WOKE_GATEKEEPER",
                    "car": car_id,
                    "gatekeeper_state": self.gatekeeper_state,
                    "waiting_chairs": list(self.waiting_chairs),
                    "message": f"Gatekeeper was SLEEPING! Car {car_id} rings buzzer, wakes gatekeeper, and begins entry check."
                }
            elif len(self.waiting_chairs) < self.waiting_chairs_capacity:
                self.waiting_chairs.append(car_id)
                return {
                    "success": True,
                    "action": "WAITING_IN_CHAIR",
                    "car": car_id,
                    "gatekeeper_state": self.gatekeeper_state,
                    "waiting_chairs": list(self.waiting_chairs),
                    "message": f"Gatekeeper is busy servicing {self.currently_servicing}. Car {car_id} takes waiting chair ({len(self.waiting_chairs)}/{self.waiting_chairs_capacity})."
                }
            else:
                return {
                    "success": False,
                    "action": "BALKED_LEFT",
                    "car": car_id,
                    "gatekeeper_state": self.gatekeeper_state,
                    "waiting_chairs": list(self.waiting_chairs),
                    "message": f"NO WAITING SPACE! All {self.waiting_chairs_capacity} chairs occupied. Car {car_id} balks and drives away!"
                }

    def gatekeeper_finish_service(self) -> Dict[str, Any]:
        """Gatekeeper finishes servicing current car and checks waiting chairs."""
        with self._lock:
            completed_car = self.currently_servicing
            if self.waiting_chairs:
                next_car = self.waiting_chairs.pop(0)
                self.currently_servicing = next_car
                self.gatekeeper_state = "SERVICING"
                return {
                    "success": True,
                    "action": "NEXT_CAR",
                    "completed_car": completed_car,
                    "servicing_car": next_car,
                    "waiting_chairs": list(self.waiting_chairs),
                    "message": f"Gatekeeper finished {completed_car}. Called next car {next_car} from waiting chair."
                }
            else:
                self.currently_servicing = None
                self.gatekeeper_state = "SLEEPING"
                return {
                    "success": True,
                    "action": "FALL_ASLEEP",
                    "completed_car": completed_car,
                    "gatekeeper_state": "SLEEPING",
                    "waiting_chairs": [],
                    "message": f"No more waiting cars! Gatekeeper falls asleep in booth until next vehicle arrives."
                }

    # --- DINING PHILOSOPHERS ROUNDABOUT METHODS ---
    def trigger_roundabout_deadlock(self) -> Dict[str, Any]:
        """Demonstrates classical deadlock: all 5 cars grab their left road segment simultaneously."""
        with self._lock:
            self.philosopher_states = ["HUNGRY"] * 5
            self.forks_held = [0, 1, 2, 3, 4]  # Each car i holds segment i
            return {
                "deadlock": True,
                "states": list(self.philosopher_states),
                "held_segments": [f"Car {i} holds Segment {i} and WAITS for Segment {(i+1)%5}" for i in range(5)],
                "message": "CIRCULAR WAIT DEADLOCK! All 5 vehicles acquired their left segment simultaneously. None can acquire right segment. System is permanently frozen!",
                "coffman_conditions_met": ["Mutual Exclusion", "Hold and Wait", "No Preemption", "Circular Wait"]
            }

    def resolve_roundabout_deadlock(self) -> Dict[str, Any]:
        """Applies Dijkstra's / Asymmetric resource hierarchy solution to prevent deadlock."""
        with self._lock:
            # Car 4 is asymmetric: picks up right segment first, or cars take both atomically
            self.philosopher_states = ["EATING", "THINKING", "EATING", "THINKING", "THINKING"]
            self.forks_held = ["Car 0", "Car 0", "Car 2", "Car 2", "FREE"]
            return {
                "deadlock": False,
                "states": list(self.philosopher_states),
                "message": "DEADLOCK AVERTED via Asymmetric Resource Ordering! Car 0 and Car 2 cross roundabout safely without circular wait.",
                "solution": "Resource Hierarchy Rule: Process must request lowest-numbered resource first, breaking circular wait."
            }

    def get_state(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "producer_consumer": {
                    "buffer": list(self.buffer_queue),
                    "capacity": self.buffer_capacity,
                    "history": self.pc_history[-5:]
                },
                "reader_writer": {
                    "active_readers": list(self.active_readers),
                    "active_writer": self.active_writer,
                    "slot_count": self.rw_slot_count,
                    "read_count": self.read_count
                },
                "sleeping_barber": {
                    "state": self.gatekeeper_state,
                    "servicing": self.currently_servicing,
                    "waiting_chairs": list(self.waiting_chairs),
                    "capacity": self.waiting_chairs_capacity
                },
                "dining_philosophers": {
                    "states": list(self.philosopher_states),
                    "forks": list(self.forks_held)
                }
            }
