"""
NEXUS-PARK // Commercial Parking Management System & OS Simulation Models
Course: Operating Systems (CCSE0303A) - Unit 2 & Unit 3
Team: Group 7 (NIET Greater Noida)
"""

from enum import Enum
import time
from typing import Optional, Dict, Any, List


class ProcessState(str, Enum):
    NEW = "NEW"                 # Vehicle request generated at entry gate
    READY = "READY"             # Vehicle validated, waiting for scheduler/slot
    RUNNING = "RUNNING"         # In critical section / slot allocation & parking active
    WAITING = "WAITING"         # Blocked on unavailable slot or semaphore
    TERMINATED = "TERMINATED"   # Slot released, bill settled, vehicle exited


class VehicleType(str, Enum):
    EMERGENCY = "EMERGENCY"     # Priority 1 (Ambulance, Police, Fire)
    EV = "EV"                   # Priority 2 (Electric Vehicle - Needs Charging Bay)
    SUV = "SUV"                 # Priority 3 (Heavy Vehicle / SUV)
    STANDARD = "STANDARD"       # Priority 4 (Compact / Sedan / Hatchback)


class ParkingSlotType(str, Enum):
    COMPACT = "COMPACT"         # Standard vehicles
    EV_CHARGING = "EV_CHARGING" # Electric vehicles with charging station
    SUV_HEAVY = "SUV_HEAVY"     # Heavy vehicles / SUVs
    VALET = "VALET"             # Emergency / VIP / Valet reserved bay


class SlotStatus(str, Enum):
    FREE = "FREE"
    OCCUPIED = "OCCUPIED"
    RESERVED = "RESERVED"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"
    IN_CRITICAL_SECTION = "IN_CRITICAL_SECTION"


class ReservationStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    CHECKED_IN = "CHECKED_IN"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class PricingRules:
    def __init__(
        self,
        base_hourly_rate: float = 30.0,
        ev_hourly_rate: float = 40.0,
        suv_hourly_rate: float = 35.0,
        emergency_rate: float = 0.0,
        grace_period_min: float = 15.0,
        daily_maximum: float = 350.0
    ):
        self.base_hourly_rate = base_hourly_rate
        self.ev_hourly_rate = ev_hourly_rate
        self.suv_hourly_rate = suv_hourly_rate
        self.emergency_rate = emergency_rate
        self.grace_period_min = grace_period_min
        self.daily_maximum = daily_maximum

    def calculate_fee(self, duration_min: float, vehicle_type: VehicleType) -> float:
        if vehicle_type == VehicleType.EMERGENCY:
            return 0.0
        if duration_min <= self.grace_period_min:
            return 0.0
        hrs = max(1.0, duration_min / 60.0)
        rate = self.base_hourly_rate
        if vehicle_type == VehicleType.EV:
            rate = self.ev_hourly_rate
        elif vehicle_type == VehicleType.SUV:
            rate = self.suv_hourly_rate
        return round(min(self.daily_maximum, hrs * rate), 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "base_hourly_rate": self.base_hourly_rate,
            "ev_hourly_rate": self.ev_hourly_rate,
            "suv_hourly_rate": self.suv_hourly_rate,
            "emergency_rate": self.emergency_rate,
            "grace_period_min": self.grace_period_min,
            "daily_maximum": self.daily_maximum
        }


class PaymentRecord:
    def __init__(
        self,
        transaction_id: str,
        session_id: str,
        plate: str,
        amount: float,
        payment_method: str = "FASTTAG",
        status: str = "COMPLETED",
        timestamp: Optional[float] = None
    ):
        self.transaction_id = transaction_id
        self.session_id = session_id
        self.plate = plate
        self.amount = round(amount, 2)
        self.payment_method = payment_method
        self.status = status
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.receipt_number = f"RCP-{int(time.time() * 1000) % 1000000:06d}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "session_id": self.session_id,
            "receipt_number": self.receipt_number,
            "plate": self.plate,
            "amount": self.amount,
            "payment_method": self.payment_method,
            "status": self.status,
            "timestamp": round(self.timestamp, 2)
        }


class Reservation:
    def __init__(
        self,
        reservation_id: str,
        customer_name: str,
        customer_phone: str,
        plate: str,
        vehicle_type: VehicleType,
        slot_id: str,
        start_time_str: str,
        duration_hours: float = 2.0,
        status: ReservationStatus = ReservationStatus.CONFIRMED,
        notes: str = ""
    ):
        self.reservation_id = reservation_id
        self.customer_name = customer_name
        self.customer_phone = customer_phone
        self.plate = plate
        self.vehicle_type = vehicle_type
        self.slot_id = slot_id
        self.start_time_str = start_time_str
        self.duration_hours = duration_hours
        self.status = status
        self.notes = notes
        self.created_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reservation_id": self.reservation_id,
            "customer_name": self.customer_name,
            "customer_phone": self.customer_phone,
            "plate": self.plate,
            "vehicle_type": self.vehicle_type.value,
            "slot_id": self.slot_id,
            "start_time_str": self.start_time_str,
            "duration_hours": self.duration_hours,
            "status": self.status.value,
            "notes": self.notes,
            "created_at": round(self.created_at, 2)
        }


class ProcessControlBlock:
    """
    Process Control Block (PCB) representing a Vehicle Parking Request Task
    as defined in Operating Systems Unit 2 (Process Management).
    """

    def __init__(
        self,
        pid: str,
        plate: str,
        vehicle_type: VehicleType,
        priority: int,
        arrival_time: float,
        parking_duration_min: float,
        memory_footprint: int = 64,
        payment_mode: str = "FASTTAG",
        burst_time: Optional[float] = None,
        operator: str = "Self-Service Kiosk",
        session_id: Optional[str] = None
    ):
        self.pid = pid
        self.plate = plate
        self.vehicle_type = vehicle_type
        self.priority = priority
        self.arrival_time = arrival_time
        self.parking_duration_min = float(parking_duration_min)
        if burst_time is not None:
            self.burst_time = float(burst_time)
        else:
            self.burst_time = float(parking_duration_min)
        self.remaining_time = self.burst_time
        self.payment_mode = payment_mode
        self.state = ProcessState.NEW
        self.slot_id: Optional[str] = None
        self.operator = operator
        self.session_id = session_id or f"SESS-{pid}"
        
        # Timing & Metrics
        self.start_time: Optional[float] = None
        self.completion_time: Optional[float] = None
        self.waiting_time: float = 0.0
        self.turnaround_time: float = 0.0
        self.context_switches: int = 0
        self.fee_charged: float = 0.0
        
        # OS Simulation Context (Preserved for Academic Demo)
        self.memory_footprint = memory_footprint
        self.registers = {
            "PC": f"0x{int(arrival_time * 100) % 0xFFFF:04X}",
            "SP": "0x7FFF",
            "ACC": priority,
            "STATUS": "0x0001"
        }
        self.created_timestamp = time.time()

    def update_state(self, new_state: ProcessState):
        self.state = new_state
        if new_state == ProcessState.RUNNING and self.start_time is None:
            self.start_time = self.arrival_time

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pid": self.pid,
            "session_id": self.session_id,
            "plate": self.plate,
            "vehicle_type": self.vehicle_type.value,
            "priority": self.priority,
            "arrival_time": round(self.arrival_time, 2),
            "parking_duration_min": round(self.parking_duration_min, 2),
            "burst_time": round(self.burst_time, 2),
            "remaining_time": round(max(0.0, self.remaining_time), 2),
            "payment_mode": self.payment_mode,
            "state": self.state.value,
            "slot_id": self.slot_id,
            "operator": self.operator,
            "fee_charged": self.fee_charged,
            "start_time": round(self.start_time, 2) if self.start_time is not None else None,
            "completion_time": round(self.completion_time, 2) if self.completion_time is not None else None,
            "waiting_time": round(self.waiting_time, 2),
            "turnaround_time": round(self.turnaround_time, 2),
            "context_switches": self.context_switches,
            "memory_footprint": self.memory_footprint,
            "registers": self.registers
        }


class ParkingSlot:
    """
    Parking Slot treated as a bounded shared OS Resource & Commercial Bay.
    """

    def __init__(self, slot_id: str, slot_type: ParkingSlotType, bay_number: int):
        self.slot_id = slot_id
        self.slot_type = slot_type
        self.bay_number = bay_number
        self.status = SlotStatus.FREE
        self.current_pid: Optional[str] = None
        self.current_plate: Optional[str] = None
        self.allocated_at: Optional[float] = None
        self.total_vehicles_served: int = 0
        self.assigned_reservation_id: Optional[str] = None
        self.maintenance_reason: Optional[str] = None

    def allocate(self, pcb: ProcessControlBlock, current_time: float) -> bool:
        if self.status != SlotStatus.FREE and self.status != SlotStatus.RESERVED:
            return False
        self.status = SlotStatus.OCCUPIED
        self.current_pid = pcb.pid
        self.current_plate = pcb.plate
        self.allocated_at = current_time
        self.total_vehicles_served += 1
        pcb.slot_id = self.slot_id
        return True

    def release(self) -> Optional[str]:
        pid = self.current_pid
        self.status = SlotStatus.FREE
        self.current_pid = None
        self.current_plate = None
        self.allocated_at = None
        self.assigned_reservation_id = None
        self.maintenance_reason = None
        return pid

    def set_out_of_service(self, reason: str = "Maintenance / Cleaning"):
        self.status = SlotStatus.OUT_OF_SERVICE
        self.maintenance_reason = reason

    def set_available(self):
        self.status = SlotStatus.FREE
        self.maintenance_reason = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "slot_id": self.slot_id,
            "slot_type": self.slot_type.value,
            "bay_number": self.bay_number,
            "status": self.status.value,
            "current_pid": self.current_pid,
            "current_plate": self.current_plate,
            "allocated_at": round(self.allocated_at, 2) if self.allocated_at is not None else None,
            "total_vehicles_served": self.total_vehicles_served,
            "assigned_reservation_id": self.assigned_reservation_id,
            "maintenance_reason": self.maintenance_reason
        }
