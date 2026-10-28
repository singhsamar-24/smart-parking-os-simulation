"""
NEXUS-PARK // Commercial Parking Management Platform & OS Simulation Server
Course: Operating Systems (CCSE0303A) - Unit 2 & Unit 3
Institution: NIET Greater Noida, CSE-AI (Group 7)
"""

import sys
import os

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import json
import time
import random
import webbrowser
import threading
from typing import Dict, Any, List, Optional
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Import backend simulation components
from backend.parking_system import SmartParkingSystem
from backend.models import VehicleType
from backend.scheduler import SchedulingEngine

# Port configuration
DEFAULT_PORT = 8000
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


class SmartParkingAPIHandler(SimpleHTTPRequestHandler):
    system: SmartParkingSystem = None  # Injected by server

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Commercial API Endpoints
        if path == "/api/status":
            self._send_json(self.system.get_system_state())
        elif path == "/api/reservations":
            self._send_json({"success": True, "reservations": [r.to_dict() for r in self.system.reservations.values()]})
        elif path == "/api/payments":
            self._send_json({"success": True, "payments": [p.to_dict() for p in self.system.payments]})
        elif path == "/api/pricing":
            self._send_json({"success": True, "pricing": self.system.pricing_rules.to_dict()})
        elif path == "/api/reports/summary":
            state = self.system.get_system_state()
            durations = [p.get("turnaround_time", 15) for p in state["terminated_processes"]]
            if not durations:
                durations = [12, 18, 25, 30, 45]
            summary = {
                "daily_entries": state["stats"]["daily_entries"],
                "daily_exits": state["stats"]["daily_exits"],
                "daily_revenue": state["stats"]["daily_revenue"],
                "occupancy_pct": state["stats"]["utilization_pct"],
                "active_parked": state["stats"]["occupied_slots"],
                "available_spaces": state["stats"]["free_slots"],
                "total_capacity": state["stats"]["total_slots"],
                "duration_distribution": {
                    "under_30m": sum(1 for d in durations if d <= 30),
                    "30m_to_60m": sum(1 for d in durations if 30 < d <= 60),
                    "over_60m": sum(1 for d in durations if d > 60)
                },
                "payment_breakdown": {
                    "FASTTAG": sum(p.amount for p in self.system.payments if p.payment_method == "FASTTAG"),
                    "CARD": sum(p.amount for p in self.system.payments if p.payment_method == "CARD"),
                    "CASH": sum(p.amount for p in self.system.payments if p.payment_method == "CASH"),
                    "UPI": sum(p.amount for p in self.system.payments if p.payment_method == "UPI")
                }
            }
            self._send_json({"success": True, "report": summary})

        # Academic OS Lab Endpoints
        elif path == "/api/scheduler/compare":
            all_p = [p.to_dict() for p in self.system.ready_queue] + [p.to_dict() for p in self.system.running_processes.values()]
            if not all_p:
                all_p = [
                    {"pid": "P1", "plate": "DL-01-A1", "burst_time": 4.0, "arrival_time": 0.0, "priority": 2},
                    {"pid": "P2", "plate": "HR-26-B2", "burst_time": 3.0, "arrival_time": 1.0, "priority": 1},
                    {"pid": "P3", "plate": "UP-16-C3", "burst_time": 5.0, "arrival_time": 2.0, "priority": 4},
                    {"pid": "P4", "plate": "DL-02-D4", "burst_time": 2.0, "arrival_time": 3.0, "priority": 3},
                ]
            comparison = SchedulingEngine.compare_all(all_p, quantum=self.system.time_quantum)
            self._send_json({"success": True, "comparison": comparison, "process_count": len(all_p)})
        elif path == "/api/concurrency/peterson":
            self._send_json(self.system.concurrency_lab.trace_petersons_algorithm())
        elif path == "/api/concurrency/tsl":
            self._send_json(self.system.concurrency_lab.trace_test_and_set())
        elif path == "/api/bankers/safety":
            self._send_json(self.system.bankers_engine.run_safety_algorithm())
        elif path == "/api/classical/state":
            self._send_json(self.system.classical_lab.get_state())
        else:
            if path == "/" or path == "":
                self.path = "/index.html"
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        # 1. Commercial Vehicle Ingestion / Entry
        if path in ("/api/vehicle/entry", "/api/vehicle/add"):
            plate = body.get("plate")
            vtype_str = body.get("vehicle_type", "STANDARD")
            vtype = getattr(VehicleType, vtype_str, VehicleType.STANDARD)
            prio = body.get("priority")
            payment_mode = body.get("payment_mode", "FASTTAG")
            parking_duration_min = body.get("parking_duration_min")
            burst_time = body.get("burst_time")
            operator = body.get("operator", "Gate Attendant")
            requested_slot_id = body.get("slot_id") or body.get("requested_slot_id")

            try:
                pcb = self.system.add_vehicle(
                    plate=plate,
                    vehicle_type=vtype,
                    priority=prio,
                    parking_duration_min=float(parking_duration_min) if parking_duration_min is not None else None,
                    payment_mode=payment_mode,
                    burst_time=float(burst_time) if burst_time is not None else None,
                    operator=operator,
                    requested_slot_id=requested_slot_id
                )
                self._send_json({"success": True, "pcb": pcb.to_dict(), "message": f"Vehicle {pcb.plate} processed into {pcb.slot_id or 'allocation queue'}."})
            except ValueError as ve:
                self._send_json({"success": False, "error": str(ve)})

        # 2. Commercial Vehicle Exit & Payment Settlement
        elif path in ("/api/vehicle/exit", "/api/slot/release"):
            slot_id = body.get("slot_id")
            payment_method = body.get("payment_method", "CASH")
            result = self.system.manual_release_slot(slot_id, payment_method)
            if result:
                self._send_json({"success": True, "exit_summary": result})
            else:
                self._send_json({"success": False, "error": f"Space {slot_id} is either empty or invalid."})

        # 3. Space Out-of-Service / Maintenance Toggle
        elif path == "/api/slot/maintenance":
            slot_id = body.get("slot_id")
            out_of_service = bool(body.get("out_of_service", True))
            reason = body.get("reason", "Routine Bay Cleaning")
            try:
                res = self.system.toggle_slot_maintenance(slot_id, out_of_service, reason)
                self._send_json({"success": res, "slot_id": slot_id, "out_of_service": out_of_service})
            except ValueError as ve:
                self._send_json({"success": False, "error": str(ve)})

        # 4. Reservations Management
        elif path == "/api/reservations/create":
            try:
                res = self.system.create_reservation(
                    customer_name=body.get("customer_name", "Valued Guest"),
                    customer_phone=body.get("customer_phone", "+91 98000 00000"),
                    plate=body.get("plate", "DL-01-RES"),
                    vehicle_type=getattr(VehicleType, body.get("vehicle_type", "STANDARD"), VehicleType.STANDARD),
                    slot_id=body.get("slot_id", "S07"),
                    start_time_str=body.get("start_time_str", "Today 15:00"),
                    duration_hours=float(body.get("duration_hours", 2.0)),
                    notes=body.get("notes", "")
                )
                self._send_json({"success": True, "reservation": res.to_dict()})
            except ValueError as ve:
                self._send_json({"success": False, "error": str(ve)})

        elif path == "/api/reservations/cancel":
            res_id = body.get("reservation_id")
            success = self.system.cancel_reservation(res_id)
            self._send_json({"success": success, "reservation_id": res_id})

        elif path == "/api/reservations/checkin":
            res_id = body.get("reservation_id")
            pay_mode = body.get("payment_mode", "FASTTAG")
            try:
                pcb = self.system.checkin_reservation(res_id, pay_mode)
                self._send_json({"success": True, "pcb": pcb.to_dict(), "message": f"Reservation {res_id} admitted to bay {pcb.slot_id}."})
            except ValueError as ve:
                self._send_json({"success": False, "error": str(ve)})

        # 5. Pricing Configuration Update
        elif path == "/api/pricing/update":
            rules = self.system.pricing_rules
            if "base_hourly_rate" in body: rules.base_hourly_rate = float(body["base_hourly_rate"])
            if "ev_hourly_rate" in body: rules.ev_hourly_rate = float(body["ev_hourly_rate"])
            if "suv_hourly_rate" in body: rules.suv_hourly_rate = float(body["suv_hourly_rate"])
            if "grace_period_min" in body: rules.grace_period_min = float(body["grace_period_min"])
            if "daily_maximum" in body: rules.daily_maximum = float(body["daily_maximum"])
            self._send_json({"success": True, "pricing": rules.to_dict()})

        # 6. Academic OS Lab Endpoints
        elif path == "/api/scheduler/set":
            algo = body.get("algorithm", "FCFS")
            quantum = float(body.get("time_quantum", 2.0))
            self.system.active_scheduler = algo
            self.system.time_quantum = quantum
            self._send_json({"success": True, "active_scheduler": algo, "time_quantum": quantum})

        elif path == "/api/scheduler/compare":
            procs = body.get("processes")
            quantum = float(body.get("time_quantum", 2.0))
            if not procs:
                all_p = [p.to_dict() for p in self.system.ready_queue] + [p.to_dict() for p in self.system.running_processes.values()]
                if not all_p:
                    all_p = [
                        {"pid": "P1", "plate": "DL-01-A100", "arrival_time": 0, "burst_time": 6, "priority": 3},
                        {"pid": "P2", "plate": "UP-16-B200", "arrival_time": 1, "burst_time": 4, "priority": 1},
                        {"pid": "P3", "plate": "HR-26-C300", "arrival_time": 2, "burst_time": 8, "priority": 4},
                        {"pid": "P4", "plate": "DL-04-D400", "arrival_time": 3, "burst_time": 3, "priority": 2},
                        {"pid": "P5", "plate": "KA-05-E500", "arrival_time": 4, "burst_time": 5, "priority": 2}
                    ]
                procs = all_p
            comparison = SchedulingEngine.compare_all(procs, quantum=quantum)
            self._send_json({"success": True, "comparison": comparison})

        elif path == "/api/concurrency/race":
            mode = body.get("mode", "unsync")
            slot_id = body.get("slot_id", "S05")
            v_a = body.get("vehicle_a", "Vehicle-A (P101)")
            v_b = body.get("vehicle_b", "Vehicle-B (P102)")
            if mode == "unsync":
                res = self.system.concurrency_lab.simulate_race_condition(slot_id, v_a, v_b)
            else:
                res = self.system.concurrency_lab.simulate_synchronized_allocation(slot_id, v_a, v_b)
            self._send_json(res)

        elif path == "/api/concurrency/semaphore":
            action = body.get("action", "WAIT")
            pid = body.get("pid", "P-Req")
            res = self.system.concurrency_lab.counting_semaphore_action(action, pid)
            self._send_json(res)

        elif path == "/api/bankers/safety":
            res = self.system.bankers_engine.run_safety_algorithm()
            self._send_json(res)

        elif path == "/api/bankers/request":
            p_idx = int(body.get("process_idx", 0))
            req = body.get("request", [1, 0, 1, 0])
            res = self.system.bankers_engine.request_resources(p_idx, req)
            self._send_json(res)

        elif path == "/api/bankers/rag":
            nodes = body.get("nodes", ["P0", "P1", "P2", "R0", "R1", "R2"])
            edges = [tuple(e) for e in body.get("edges", [["P0", "R0"], ["R0", "P1"], ["P1", "R1"], ["R1", "P2"], ["P2", "R0"]])]
            res = self.system.bankers_engine.detect_rag_deadlock(nodes, edges)
            self._send_json(res)

        elif path == "/api/classical/action":
            subsystem = body.get("subsystem")
            action = body.get("action")
            cl = self.system.classical_lab

            if subsystem == "producer_consumer":
                if action == "produce":
                    vid = body.get("vehicle_id", f"Car-{len(cl.buffer_queue)+1:02d}")
                    res = cl.produce_vehicle(vid)
                else:
                    res = cl.consume_vehicle()
            elif subsystem == "reader_writer":
                if action == "start_read":
                    rid = body.get("reader_id", "Sign-North")
                    res = cl.start_read(rid)
                elif action == "stop_read":
                    rid = body.get("reader_id", "Sign-North")
                    res = cl.stop_read(rid)
                elif action == "start_write":
                    wid = body.get("writer_id", "Gate-Entry")
                    count = int(body.get("slot_count", 12))
                    res = cl.start_write(wid, count)
                else:
                    res = cl.stop_write()
            elif subsystem == "sleeping_barber":
                if action == "arrive":
                    cid = body.get("car_id", f"Car-{random.randint(100, 999)}")
                    res = cl.arrive_at_gate(cid)
                else:
                    res = cl.gatekeeper_finish_service()
            elif subsystem == "dining_philosophers":
                if action == "deadlock":
                    res = cl.trigger_roundabout_deadlock()
                else:
                    res = cl.resolve_roundabout_deadlock()
            else:
                res = {"error": f"Unknown subsystem {subsystem}"}

            self._send_json(res)

        elif path == "/api/simulation/control":
            action = body.get("action")
            if action == "pause":
                self.system.is_running = False
            elif action == "play":
                self.system.is_running = True
            elif action == "set_speed":
                self.system.speed_multiplier = float(body.get("speed", 1.0))
            elif action == "reset":
                self.system.simulation_time = 0.0
                self.system.ready_queue.clear()
                self.system.waiting_queue.clear()
                self.system.running_processes.clear()
                self.system.terminated_processes.clear()
                for slot in self.system.slots.values():
                    slot.release()
                self.system._populate_initial_state()
                self.system._populate_initial_reservations()
            self._send_json({"success": True, "state": self.system.get_system_state()})

        else:
            self.send_error(404, "Endpoint Not Found")

    def _read_json_body(self) -> Dict[str, Any]:
        try:
            content_len = int(self.headers.get("Content-Length", 0))
            if content_len > 0:
                raw_data = self.rfile.read(content_len).decode("utf-8")
                return json.loads(raw_data)
        except Exception:
            pass
        return {}

    def _send_json(self, data: Any):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        return


def run_server(port: int = DEFAULT_PORT):
    parking_system = SmartParkingSystem()
    SmartParkingAPIHandler.system = parking_system

    server_address = ("", port)
    try:
        httpd = HTTPServer(server_address, SmartParkingAPIHandler)
    except OSError:
        port = port + 1
        server_address = ("", port)
        httpd = HTTPServer(server_address, SmartParkingAPIHandler)

    url = f"http://localhost:{port}"

    banner = (
        "=" * 76 + "\n"
        " [P] NEXUS-PARK // COMMERCIAL PARKING MANAGEMENT SYSTEM & OS LAB\n"
        " Facility    : Metro Central Facility - Terminal Deck A (16 Bays)\n"
        " Platform    : Commercial SaaS Operator Console + Academic OS Simulation\n"
        " Department  : CSE-AI, NIET Greater Noida (Group 7 - CCSE0303A)\n"
        " Team        : Ishank Rana, Chhavi Attri, Aditi Singh,\n"
        "               Pratyush Agrahari, Samar Singh\n"
        " Faculty     : Mr. Amar Pal Yadav & Dr. Varsha Jotwani\n"
        + "=" * 76
    )
    print(banner)
    print(f" [+] HTTP Server listening on port {port}")
    print(f" [+] Launching Commercial SaaS Console: {url}")
    print(" [+] Press Ctrl+C in terminal to stop server.")
    print("=" * 76)

    def open_browser():
        time.sleep(1.0)
        try:
            webbrowser.open(url)
        except Exception:
            pass

    threading.Thread(target=open_browser, daemon=True).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Shutting down server gracefully...")
        httpd.server_close()
        sys.exit(0)


if __name__ == "__main__":
    port_arg = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    run_server(port_arg)
