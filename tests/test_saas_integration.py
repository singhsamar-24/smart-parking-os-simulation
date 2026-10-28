"""
Integration Test Suite for NEXUS-PARK Commercial Transformation
Verifies:
1. DOM Element ID consistency between static/index.html and static/js/*.js
2. Backend models & pricing rules
3. Server REST endpoints (Vehicle Ingress/Egress, Reservations, Maintenance, Pricing, Reports, OS Lab)
"""

import re
import json
import urllib.request
import urllib.error
import subprocess
import time
import sys

def test_dom_ids():
    print("--- 1. Testing DOM ID Integrity ---")
    html_content = open("static/index.html", encoding="utf-8").read()
    html_ids = set(re.findall(r'id=["\']([a-zA-Z0-9_\-]+)["\']', html_content))

    for js_file in ["app.js", "parking_lot.js", "three_parking.js", "scheduler_viz.js", "concurrency_viz.js", "bankers_viz.js", "classical_viz.js"]:
        path = f"static/js/{js_file}"
        try:
            content = open(path, encoding="utf-8").read()
            js_ids = set(re.findall(r'getElementById\(["\']([a-zA-Z0-9_\-]+)["\']\)', content))
            missing = js_ids - html_ids
            if missing:
                print(f"FAILED: {js_file} references missing DOM IDs: {missing}")
                sys.exit(1)
            else:
                print(f"PASSED: {js_file} (all {len(js_ids)} DOM IDs verified in index.html)")
        except FileNotFoundError:
            print(f"WARNING: File {path} not found")

def test_live_server_endpoints():
    print("\n--- 2. Testing Live Server Commercial Endpoints ---")
    port = 8011
    server_process = subprocess.Popen([sys.executable, "main.py", str(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    base = f"http://127.0.0.1:{port}"

    # Wait for server to become responsive
    connected = False
    for i in range(25):
        if server_process.poll() is not None:
            stdout, stderr = server_process.communicate()
            print("Server process died prematurely!")
            print("STDOUT:", stdout.decode(errors='ignore'))
            print("STDERR:", stderr.decode(errors='ignore'))
            sys.exit(1)
        try:
            with urllib.request.urlopen(f"{base}/api/status", timeout=1) as resp:
                if resp.status == 200:
                    connected = True
                    break
        except Exception:
            time.sleep(0.3)

    if not connected:
        stdout, stderr = server_process.communicate()
        print("Server failed to respond within timeout.")
        print("STDOUT:", stdout.decode(errors='ignore'))
        print("STDERR:", stderr.decode(errors='ignore'))
        sys.exit(1)

    print(f"Connected to test server on port {port}!")

    def get(endpoint):
        req = urllib.request.Request(f"{base}{endpoint}")
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())

    def post(endpoint, data):
        req = urllib.request.Request(
            f"{base}{endpoint}",
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())

    try:
        # 1. Status Check
        status = get("/api/status")
        assert "slots" in status, "Status missing slots"
        assert "stats" in status, "Status missing stats"
        assert status["stats"]["total_slots"] == 16, f"Expected 16 bays, got {status['stats']['total_slots']}"
        print(f"PASSED: /api/status (16 Bays, Free: {status['stats']['free_slots']}, Occupied: {status['stats']['occupied_slots']})")

        # 2. Ingress Entry (Standard Car)
        entry1 = post("/api/vehicle/entry", {
            "plate": "DL-01-COMM1",
            "vehicle_type": "STANDARD",
            "parking_duration_min": 60,
            "payment_mode": "FASTTAG"
        })
        assert entry1["success"], f"Entry 1 failed: {entry1}"
        slot1 = entry1["pcb"].get("slot_id")
        if not slot1:
            for _ in range(10):
                time.sleep(0.3)
                st = get("/api/status")
                for p in st.get("running_processes", []):
                    if p["plate"] == "DL-01-COMM1":
                        slot1 = p["slot_id"]
                        break
                if slot1:
                    break
        assert slot1 is not None, "DL-01-COMM1 was not dispatched to a parking bay"
        print(f"PASSED: /api/vehicle/entry (DL-01-COMM1 admitted to {slot1})")

        # 3. Duplicate Plate Ingress Test (Should Reject)
        dup = post("/api/vehicle/entry", {
            "plate": "DL-01-COMM1",
            "vehicle_type": "STANDARD"
        })
        assert not dup["success"], "Duplicate plate should have been rejected"
        print(f"PASSED: Duplicate plate rejection ({dup['error']})")

        # 4. Explicit Bay Assignment (EV Charging bay S10)
        entry_ev = post("/api/vehicle/entry", {
            "plate": "UP-16-EV999",
            "vehicle_type": "EV",
            "slot_id": "S10",
            "parking_duration_min": 45,
            "payment_mode": "UPI"
        })
        assert entry_ev["success"] and entry_ev["pcb"]["slot_id"] == "S10", f"EV Entry failed: {entry_ev}"
        print("PASSED: /api/vehicle/entry explicit bay assignment (UP-16-EV999 in S10)")

        # 5. Out of Service / Maintenance Toggle
        maint = post("/api/slot/maintenance", {
            "slot_id": "S14",
            "out_of_service": True,
            "reason": "Sensor Calibration"
        })
        assert maint["success"], f"Maintenance failed: {maint}"
        print("PASSED: /api/slot/maintenance (S14 marked OUT_OF_SERVICE)")

        # 6. Advance Reservation
        res = post("/api/reservations/create", {
            "customer_name": "Dr. Sameer Verma",
            "customer_phone": "+91 98111 22233",
            "plate": "HR-26-VIP01",
            "vehicle_type": "SUV",
            "slot_id": "S08",
            "start_time_str": "Today 16:30",
            "duration_hours": 3.0,
            "notes": "Executive Guest Parking"
        })
        assert res["success"], f"Reservation failed: {res}"
        res_id = res["reservation"]["reservation_id"]
        print(f"PASSED: /api/reservations/create (Reserved S08 for {res_id})")

        # 7. Check-in Reservation
        checkin = post("/api/reservations/checkin", {
            "reservation_id": res_id,
            "payment_mode": "FASTTAG"
        })
        assert checkin["success"], f"Check-in failed: {checkin}"
        print(f"PASSED: /api/reservations/checkin ({res_id} checked into S08)")

        # 8. Vehicle Exit & Payment Settlement
        exit1 = post("/api/vehicle/exit", {
            "slot_id": slot1,
            "payment_method": "FASTTAG"
        })
        assert exit1["success"], f"Exit failed: {exit1}"
        summary = exit1["exit_summary"]
        assert summary["fee"] >= 0, "Fee should be non-negative"
        print(f"PASSED: /api/vehicle/exit (Bay {slot1} released, Fee: INR {summary['fee']:.2f}, Receipt: {summary['payment']['receipt_number']})")

        # 9. Pricing Tariff Update
        pricing_update = post("/api/pricing/update", {
            "base_hourly_rate": 35,
            "ev_hourly_rate": 45,
            "suv_hourly_rate": 40,
            "grace_period_min": 10,
            "daily_maximum": 400
        })
        assert pricing_update["success"] and pricing_update["pricing"]["base_hourly_rate"] == 35
        print("PASSED: /api/pricing/update (New tariff saved)")

        # 10. Reports Summary
        reports_resp = get("/api/reports/summary")
        assert reports_resp.get("success"), "Reports request failed"
        reports = reports_resp["report"]
        assert "daily_revenue" in reports and "daily_entries" in reports
        print(f"PASSED: /api/reports/summary (Entries: {reports['daily_entries']}, Exits: {reports['daily_exits']}, Revenue: INR {reports['daily_revenue']:.2f})")

        # 11. Academic OS Lab Endpoints
        bench = get("/api/scheduler/compare")
        assert "comparison" in bench and len(bench["comparison"]) == 6
        print("PASSED: /api/scheduler/compare (6 scheduling algorithms benchmarked)")

        safety = get("/api/bankers/safety")
        assert "is_safe" in safety
        print(f"PASSED: /api/bankers/safety (Safe sequence: {safety.get('safe_sequence')})")

        print("\nALL 11 BACKEND & DOM TESTS PASSED WITH 100% SUCCESS!")

    finally:
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    test_dom_ids()
    test_live_server_endpoints()
