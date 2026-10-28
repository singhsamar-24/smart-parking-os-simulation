"""
NEXUS-PARK // Commercial Parking Simulation Engine & OS Kernel
Coordinates Commercial Facility Management (Overview, Live Map, Vehicles, Kiosk, Reservations, Payments, Reports)
and Academic OS Demonstrations (CPU Scheduling, Concurrency, Banker's Algorithm, Classical Sync).
"""

import threading
import time
import random
from typing import Dict, Any, List, Optional
from backend.models import (
    ProcessControlBlock, ParkingSlot, ProcessState, VehicleType,
    ParkingSlotType, SlotStatus, PricingRules, PaymentRecord,
    Reservation, ReservationStatus
)
from backend.scheduler import SchedulingEngine
from backend.concurrency import ConcurrencyLab
from backend.bankers import BankersAlgorithmEngine
from backend.classical import ClassicalSyncLab


class SmartParkingSystem:
    def __init__(self):
        self.lock = threading.RLock()
        
        # Facility Identity & Configuration
        self.facility_info = {
            "id": "FAC-01",
            "name": "NEXUS-PARK // Metro Central Hub",
            "deck": "Terminal Deck A (Bays S01–S16)",
            "location": "Sector 62, Commercial Corridor",
            "operating_status": "ONLINE_OPERATIONAL",
            "operator_name": "Ishank Rana (Lead Attendant)",
            "system_mode": "COMMERCIAL_OPERATIONS"
        }

        # Pricing & Billing Rules
        self.pricing_rules = PricingRules()
        
        # System Time & Clocks
        self.simulation_time: float = 0.0
        self.time_quantum: float = 2.0
        self.active_scheduler = "FCFS"
        self.is_running = True
        self.speed_multiplier = 1.0
        
        # 16 Commercial Parking Spaces (Shared OS Resources)
        self.slots: Dict[str, ParkingSlot] = {}
        self._initialize_slots()
        
        # Queues & Active Workload
        self.job_pool: List[ProcessControlBlock] = []
        self.ready_queue: List[ProcessControlBlock] = []
        self.waiting_queue: List[ProcessControlBlock] = []
        self.running_processes: Dict[str, ProcessControlBlock] = {}
        self.terminated_processes: List[ProcessControlBlock] = []

        # Commercial Modules: Reservations & Payments
        self.reservations: Dict[str, Reservation] = {}
        self.payments: List[PaymentRecord] = []
        self.daily_entries_count: int = 0
        self.daily_exits_count: int = 0
        
        # OS Synchronization Primitives (Preserved for Academic Demo)
        self.critical_section_lock = threading.Lock()
        self.critical_section_occupant: Optional[str] = None
        self.available_slots_semaphore = threading.Semaphore(16)
        
        # OS Academic Lab Engines
        self.concurrency_lab = ConcurrencyLab()
        self.bankers_engine = BankersAlgorithmEngine()
        self.classical_lab = ClassicalSyncLab()
        
        # Activity Logs & Counters
        self.event_logs: List[Dict[str, Any]] = []
        self.pid_counter = 100
        self.res_counter = 500
        self.txn_counter = 1000
        
        # Seed realistic initial state and reservations
        self._populate_initial_state()
        self._populate_initial_reservations()

        # Background Simulation Loop
        self.worker_thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self.worker_thread.start()

    def _initialize_slots(self):
        """Initializes 16 hardware parking bays mapped to memory segments."""
        # 8 Compact slots (S01 - S08)
        for i in range(1, 9):
            sid = f"S{i:02d}"
            self.slots[sid] = ParkingSlot(sid, ParkingSlotType.COMPACT, i)
        
        # 4 EV Charging bays (S09 - S12)
        for i in range(9, 13):
            sid = f"S{i:02d}"
            self.slots[sid] = ParkingSlot(sid, ParkingSlotType.EV_CHARGING, i)
        
        # 2 Heavy SUV slots (S13 - S14)
        for i in range(13, 15):
            sid = f"S{i:02d}"
            self.slots[sid] = ParkingSlot(sid, ParkingSlotType.SUV_HEAVY, i)
        
        # 2 Valet / Emergency slots (S15 - S16)
        for i in range(15, 17):
            sid = f"S{i:02d}"
            self.slots[sid] = ParkingSlot(sid, ParkingSlotType.VALET, i)

    def _populate_initial_state(self):
        """Creates sample vehicles demonstrating diverse commercial operations."""
        samples = [
            ("AMB-101",      VehicleType.EMERGENCY, 1, 15.0, "CASH"),
            ("EV-TESLA",     VehicleType.EV,        2, 20.0, "FASTTAG"),
            ("UP-16-7788",   VehicleType.STANDARD,  4, 12.0, "CASH"),
            ("SUV-FORTUNER", VehicleType.SUV,       3, 18.0, "CARD"),
            ("DL-3C-9900",   VehicleType.STANDARD,  4, 25.0, "FASTTAG"),
        ]
        for plate, vtype, prio, dur_min, pay in samples:
            self.add_vehicle(plate=plate, vehicle_type=vtype, priority=prio,
                             parking_duration_min=dur_min, payment_mode=pay)

    def _populate_initial_reservations(self):
        """Pre-populates realistic commercial parking reservations."""
        r1 = Reservation(
            reservation_id="RES-501",
            customer_name="Dr. Rajiv Mehta",
            customer_phone="+91 98110 44221",
            plate="DL-01-VIP001",
            vehicle_type=VehicleType.STANDARD,
            slot_id="S07",
            start_time_str="14:00 Today",
            duration_hours=3.0,
            status=ReservationStatus.CONFIRMED,
            notes="VIP Guest / Board Conference"
        )
        self.reservations[r1.reservation_id] = r1
        if "S07" in self.slots and self.slots["S07"].status == SlotStatus.FREE:
            self.slots["S07"].status = SlotStatus.RESERVED
            self.slots["S07"].assigned_reservation_id = r1.reservation_id

        r2 = Reservation(
            reservation_id="RES-502",
            customer_name="Priya Sharma",
            customer_phone="+91 99201 88310",
            plate="UP-16-EV990",
            vehicle_type=VehicleType.EV,
            slot_id="S11",
            start_time_str="16:30 Today",
            duration_hours=2.0,
            status=ReservationStatus.CONFIRMED,
            notes="Requires 22kW Fast Charger"
        )
        self.reservations[r2.reservation_id] = r2
        if "S11" in self.slots and self.slots["S11"].status == SlotStatus.FREE:
            self.slots["S11"].status = SlotStatus.RESERVED
            self.slots["S11"].assigned_reservation_id = r2.reservation_id

    def add_vehicle(
        self,
        plate: Optional[str] = None,
        vehicle_type: VehicleType = VehicleType.STANDARD,
        priority: Optional[int] = None,
        parking_duration_min: Optional[float] = None,
        payment_mode: str = "FASTTAG",
        burst_time: Optional[float] = None,
        operator: str = "Gate Attendant",
        requested_slot_id: Optional[str] = None
    ) -> ProcessControlBlock:
        with self.lock:
            # 1. Validation: Prevent duplicate active parking sessions
            if plate:
                plate = plate.strip().upper()
                for p in self.running_processes.values():
                    if p.plate.upper() == plate:
                        raise ValueError(f"Vehicle {plate} already has an active parking session in bay {p.slot_id}!")
                for p in self.ready_queue:
                    if p.plate.upper() == plate:
                        raise ValueError(f"Vehicle {plate} is already waiting in the entry queue!")

            # 2. Validation: Requested manual slot
            if requested_slot_id:
                if requested_slot_id not in self.slots:
                    raise ValueError(f"Space {requested_slot_id} does not exist.")
                target_slot = self.slots[requested_slot_id]
                if target_slot.status == SlotStatus.OCCUPIED:
                    raise ValueError(f"Space {requested_slot_id} is already occupied by {target_slot.current_plate}.")
                if target_slot.status == SlotStatus.OUT_OF_SERVICE:
                    raise ValueError(f"Space {requested_slot_id} is currently OUT OF SERVICE ({target_slot.maintenance_reason}).")

            self.pid_counter += 1
            pid = f"P{self.pid_counter}"
            
            if not plate:
                cities = ["UP-16", "DL-01", "HR-26", "MH-02", "KA-05"]
                plate = f"{random.choice(cities)}-{random.randint(1000, 9999)}"
            
            if priority is None:
                priority_map = {
                    VehicleType.EMERGENCY: 1,
                    VehicleType.EV: 2,
                    VehicleType.SUV: 3,
                    VehicleType.STANDARD: 4
                }
                priority = priority_map.get(vehicle_type, 4)

            if parking_duration_min is None:
                if burst_time is not None:
                    parking_duration_min = burst_time
                else:
                    parking_duration_min = float(random.randint(10, 30))

            pcb = ProcessControlBlock(
                pid=pid,
                plate=plate,
                vehicle_type=vehicle_type,
                priority=priority,
                arrival_time=self.simulation_time,
                parking_duration_min=parking_duration_min,
                payment_mode=payment_mode,
                burst_time=burst_time,
                operator=operator
            )

            # If an explicit valid slot was requested, allocate immediately
            if requested_slot_id and self.slots[requested_slot_id].status in (SlotStatus.FREE, SlotStatus.RESERVED):
                slot = self.slots[requested_slot_id]
                slot.allocate(pcb, self.simulation_time)
                pcb.update_state(ProcessState.RUNNING)
                pcb.waiting_time = 0.0
                self.running_processes[pcb.pid] = pcb
                self.daily_entries_count += 1
                self._log_event(
                    category="ENTRY_REGISTERED",
                    title=f"Vehicle Entry: {pcb.plate} (PID: {pcb.pid})",
                    detail=f"Directly assigned to Space {slot.slot_id} · Payment: {payment_mode}"
                )
                return pcb

            # Otherwise place into dispatcher ready queue
            pcb.update_state(ProcessState.READY)
            self.ready_queue.append(pcb)
            self.daily_entries_count += 1

            self._log_event(
                category="ENTRY_REGISTERED",
                title=f"Vehicle Arrived: {pcb.plate} (PID: {pcb.pid})",
                detail=f"Queued for space allocation · Type: {pcb.vehicle_type.value} · Est: {pcb.parking_duration_min:.0f}m"
            )
            return pcb

    def _find_suitable_slot(self, pcb: ProcessControlBlock) -> Optional[ParkingSlot]:
        """Maps vehicle requirements to an available parking space."""
        preferred_type = ParkingSlotType.COMPACT
        if pcb.vehicle_type == VehicleType.EMERGENCY:
            preferred_type = ParkingSlotType.VALET
        elif pcb.vehicle_type == VehicleType.EV:
            preferred_type = ParkingSlotType.EV_CHARGING
        elif pcb.vehicle_type == VehicleType.SUV:
            preferred_type = ParkingSlotType.SUV_HEAVY

        # 1. Preferred type match
        for slot in self.slots.values():
            if slot.status == SlotStatus.FREE and slot.slot_type == preferred_type:
                return slot
        
        # 2. Fallback to any free slot
        for slot in self.slots.values():
            if slot.status == SlotStatus.FREE:
                return slot
        
        return None

    def _simulation_loop(self):
        """Heartbeat loop driving time progression, parking duration, and release."""
        while True:
            time.sleep(0.5)
            if not self.is_running:
                continue

            with self.lock:
                dt = 0.5 * self.speed_multiplier
                self.simulation_time += dt

                # Check departures
                departed_pids = []
                for pid, pcb in list(self.running_processes.items()):
                    pcb.remaining_time -= dt
                    if pcb.remaining_time <= 0:
                        departed_pids.append(pid)

                for pid in departed_pids:
                    self._release_and_terminate(pid)

                # Dispatch incoming queues
                self._dispatch_scheduler()

    def _dispatch_scheduler(self):
        """Dispatches ready vehicles into available spaces."""
        if self.waiting_queue:
            free_count = sum(1 for s in self.slots.values() if s.status == SlotStatus.FREE)
            if free_count > 0:
                self.ready_queue.extend(self.waiting_queue)
                self.waiting_queue.clear()

        if not self.ready_queue:
            return

        if self.active_scheduler == "FCFS":
            self.ready_queue.sort(key=lambda p: (p.arrival_time, p.pid))
        elif self.active_scheduler == "SJF":
            self.ready_queue.sort(key=lambda p: (p.burst_time, p.arrival_time))
        elif self.active_scheduler == "SRTF":
            self.ready_queue.sort(key=lambda p: (p.remaining_time, p.arrival_time))
        elif "PRIORITY" in self.active_scheduler:
            self.ready_queue.sort(key=lambda p: (p.priority, p.arrival_time))

        while self.ready_queue:
            candidate = self.ready_queue[0]
            slot = self._find_suitable_slot(candidate)

            if slot:
                with self.critical_section_lock:
                    self.critical_section_occupant = candidate.pid
                    candidate = self.ready_queue.pop(0)
                    if slot.status == SlotStatus.FREE:
                        slot.allocate(candidate, self.simulation_time)
                        candidate.update_state(ProcessState.RUNNING)
                        candidate.waiting_time = max(0.0, self.simulation_time - candidate.arrival_time)
                        self.running_processes[candidate.pid] = candidate
                        self._log_event(
                            category="SPACE_OCCUPIED",
                            title=f"Space {slot.slot_id} Allocated to {candidate.plate}",
                            detail=f"Dispatched into {slot.slot_type.value} Bay (Task: {candidate.pid})"
                        )
                    else:
                        self.ready_queue.insert(0, candidate)
                    self.critical_section_occupant = None
            else:
                # No free space available — move to blocked waiting queue
                blocked = []
                remaining = []
                for p in self.ready_queue:
                    if self._find_suitable_slot(p) is None:
                        if p.state != ProcessState.WAITING:
                            p.update_state(ProcessState.WAITING)
                            self._log_event(
                                category="CAPACITY_HOLD",
                                title=f"Vehicle {p.plate} Waiting for Free Bay",
                                detail="Facility currently at full capacity for requested bay type."
                            )
                        blocked.append(p)
                    else:
                        remaining.append(p)
                self.ready_queue = remaining
                self.waiting_queue.extend(blocked)
                break

    def _release_and_terminate(self, pid: str, payment_method: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Completes parking session, computes billing, records payment, and frees space."""
        pcb = self.running_processes.pop(pid, None)
        if not pcb:
            return None

        slot_id = pcb.slot_id
        if slot_id and slot_id in self.slots:
            self.slots[slot_id].release()

        pcb.completion_time = self.simulation_time
        pcb.turnaround_time = pcb.completion_time - pcb.arrival_time
        pcb.waiting_time = max(0.0, pcb.turnaround_time - pcb.burst_time)
        pcb.update_state(ProcessState.TERMINATED)

        # Calculate Commercial Parking Fee
        duration_min = pcb.turnaround_time if pcb.turnaround_time > 0 else pcb.parking_duration_min
        fee = self.pricing_rules.calculate_fee(duration_min, pcb.vehicle_type)
        pcb.fee_charged = fee

        # Create Commercial Payment Record
        self.txn_counter += 1
        pay_method = payment_method or pcb.payment_mode or "FASTTAG"
        txn = PaymentRecord(
            transaction_id=f"TXN-{self.txn_counter}",
            session_id=pcb.session_id,
            plate=pcb.plate,
            amount=fee,
            payment_method=pay_method,
            status="COMPLETED" if fee > 0 else "EXEMPT_COMPLETED",
            timestamp=self.simulation_time
        )
        self.payments.append(txn)
        self.daily_exits_count += 1
        self.terminated_processes.append(pcb)

        self._log_event(
            category="EXIT_PROCESSED",
            title=f"Vehicle Departed: {pcb.plate} (Space {slot_id} Released)",
            detail=f"Duration: {duration_min:.1f} min · Fee: ₹{fee:.2f} · Method: {pay_method} · Receipt: {txn.receipt_number}"
        )

        return {
            "pcb": pcb.to_dict(),
            "payment": txn.to_dict(),
            "slot_id": slot_id,
            "duration_min": round(duration_min, 1),
            "fee": fee
        }

    def manual_release_slot(self, slot_id: str, payment_method: str = "CASH") -> Optional[Dict[str, Any]]:
        with self.lock:
            if slot_id in self.slots and self.slots[slot_id].status == SlotStatus.OCCUPIED:
                pid = self.slots[slot_id].current_pid
                if pid:
                    return self._release_and_terminate(pid, payment_method)
            return None

    def toggle_slot_maintenance(self, slot_id: str, out_of_service: bool, reason: str = "Maintenance / Cleaning") -> bool:
        with self.lock:
            if slot_id not in self.slots:
                return False
            slot = self.slots[slot_id]
            if slot.status == SlotStatus.OCCUPIED:
                raise ValueError(f"Cannot take Space {slot_id} out of service while occupied by {slot.current_plate}.")
            if out_of_service:
                slot.set_out_of_service(reason)
                self._log_event(
                    category="MAINTENANCE",
                    title=f"Space {slot_id} Set to OUT OF SERVICE",
                    detail=f"Reason: {reason}"
                )
            else:
                slot.set_available()
                self._log_event(
                    category="MAINTENANCE",
                    title=f"Space {slot_id} Returned to ACTIVE SERVICE",
                    detail="Available for assignment."
                )
            return True

    def create_reservation(
        self,
        customer_name: str,
        customer_phone: str,
        plate: str,
        vehicle_type: VehicleType,
        slot_id: str,
        start_time_str: str,
        duration_hours: float = 2.0,
        notes: str = ""
    ) -> Reservation:
        with self.lock:
            if slot_id not in self.slots:
                raise ValueError(f"Space {slot_id} does not exist.")
            slot = self.slots[slot_id]
            if slot.status == SlotStatus.OCCUPIED:
                raise ValueError(f"Space {slot_id} is currently occupied.")
            if slot.status == SlotStatus.OUT_OF_SERVICE:
                raise ValueError(f"Space {slot_id} is out of service.")
            if slot.status == SlotStatus.RESERVED and slot.assigned_reservation_id:
                raise ValueError(f"Space {slot_id} is already reserved by Reservation {slot.assigned_reservation_id}.")

            self.res_counter += 1
            res_id = f"RES-{self.res_counter}"
            res = Reservation(
                reservation_id=res_id,
                customer_name=customer_name,
                customer_phone=customer_phone,
                plate=plate.strip().upper(),
                vehicle_type=vehicle_type,
                slot_id=slot_id,
                start_time_str=start_time_str,
                duration_hours=duration_hours,
                status=ReservationStatus.CONFIRMED,
                notes=notes
            )
            self.reservations[res_id] = res
            slot.status = SlotStatus.RESERVED
            slot.assigned_reservation_id = res_id

            self._log_event(
                category="RESERVATION_CREATED",
                title=f"Reservation {res_id} Created ({plate})",
                detail=f"Space {slot_id} held for {customer_name} ({start_time_str})"
            )
            return res

    def cancel_reservation(self, reservation_id: str) -> bool:
        with self.lock:
            if reservation_id not in self.reservations:
                return False
            res = self.reservations[reservation_id]
            res.status = ReservationStatus.CANCELLED
            if res.slot_id in self.slots:
                slot = self.slots[res.slot_id]
                if slot.assigned_reservation_id == reservation_id:
                    slot.set_available()

            self._log_event(
                category="RESERVATION_CANCELLED",
                title=f"Reservation {reservation_id} Cancelled",
                detail=f"Space {res.slot_id} released back to general pool."
            )
            return True

    def checkin_reservation(self, reservation_id: str, payment_mode: str = "FASTTAG") -> ProcessControlBlock:
        with self.lock:
            if reservation_id not in self.reservations:
                raise ValueError(f"Reservation {reservation_id} not found.")
            res = self.reservations[reservation_id]
            if res.status != ReservationStatus.CONFIRMED:
                raise ValueError(f"Reservation {reservation_id} is already {res.status.value}.")

            res.status = ReservationStatus.CHECKED_IN
            pcb = self.add_vehicle(
                plate=res.plate,
                vehicle_type=res.vehicle_type,
                parking_duration_min=res.duration_hours * 60.0,
                payment_mode=payment_mode,
                operator="Reservation Check-In",
                requested_slot_id=res.slot_id
            )
            self._log_event(
                category="RESERVATION_CHECKIN",
                title=f"Reservation {reservation_id} Checked In",
                detail=f"Vehicle {res.plate} admitted to reserved bay {res.slot_id}."
            )
            return pcb

    def _log_event(self, category: str, title: str, detail: str):
        self.event_logs.append({
            "timestamp": round(self.simulation_time, 2),
            "clock_str": time.strftime("%H:%M:%S"),
            "category": category,
            "title": title,
            "detail": detail
        })
        if len(self.event_logs) > 60:
            self.event_logs.pop(0)

    def get_system_state(self) -> Dict[str, Any]:
        """Provides a real-time thread-safe JSON snapshot for both Commercial & OS Lab UI."""
        with self.lock:
            occupied_count = sum(1 for s in self.slots.values() if s.status == SlotStatus.OCCUPIED)
            reserved_count = sum(1 for s in self.slots.values() if s.status == SlotStatus.RESERVED)
            maintenance_count = sum(1 for s in self.slots.values() if s.status == SlotStatus.OUT_OF_SERVICE)
            total_slots = len(self.slots)
            free_count = total_slots - (occupied_count + reserved_count + maintenance_count)
            utilization = round(((occupied_count + reserved_count) / total_slots) * 100.0, 1)

            # Revenue calculation
            total_revenue = round(sum(p.amount for p in self.payments), 2)
            today_revenue = total_revenue

            # Performance telemetry
            completed = self.terminated_processes
            avg_wt = round(sum(p.waiting_time for p in completed) / len(completed), 2) if completed else 0.0
            avg_tat = round(sum(p.turnaround_time for p in completed) / len(completed), 2) if completed else 0.0

            return {
                "simulation_time": round(self.simulation_time, 2),
                "server_time_str": time.strftime("%b %d, %Y · %I:%M:%S %p"),
                "is_running": self.is_running,
                "speed_multiplier": self.speed_multiplier,
                "facility_info": self.facility_info,
                "pricing_rules": self.pricing_rules.to_dict(),
                "active_scheduler": self.active_scheduler,
                "time_quantum": self.time_quantum,
                "slots": {sid: s.to_dict() for sid, s in self.slots.items()},
                "stats": {
                    "total_slots": total_slots,
                    "occupied_slots": occupied_count,
                    "free_slots": free_count,
                    "reserved_slots": reserved_count,
                    "maintenance_slots": maintenance_count,
                    "utilization_pct": utilization,
                    "daily_entries": self.daily_entries_count,
                    "daily_exits": self.daily_exits_count,
                    "daily_revenue": today_revenue,
                    "total_payments_count": len(self.payments),
                    "ready_queue_len": len(self.ready_queue),
                    "waiting_queue_len": len(self.waiting_queue),
                    "running_count": len(self.running_processes),
                    "terminated_count": len(self.terminated_processes),
                    "avg_waiting_time": avg_wt,
                    "avg_turnaround_time": avg_tat
                },
                "reservations": [r.to_dict() for r in self.reservations.values()],
                "payments": [p.to_dict() for p in reversed(self.payments[-20:])],
                "ready_queue": [p.to_dict() for p in self.ready_queue],
                "waiting_queue": [p.to_dict() for p in self.waiting_queue],
                "running_processes": [p.to_dict() for p in self.running_processes.values()],
                "terminated_processes": [p.to_dict() for p in self.terminated_processes[-15:]],
                "critical_section": {
                    "is_locked": self.critical_section_lock.locked(),
                    "occupant": self.critical_section_occupant
                },
                "event_logs": list(self.event_logs[-25:])
            }
