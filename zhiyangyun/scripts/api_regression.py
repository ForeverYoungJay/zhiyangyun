#!/usr/bin/env python3
import json
import sys
from datetime import date, datetime, timezone
from urllib import request, error

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/api/v1"


class Client:
    def __init__(self):
        self.token = ""
        self.results = []

    def _call(self, method: str, path: str, payload=None, expect=200):
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
        try:
            with request.urlopen(req) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                ok = resp.status == expect and body.get("success", False)
                self.results.append((method, path, ok, ""))
                return body.get("data")
        except error.HTTPError as e:
            msg = e.read().decode("utf-8")
            self.results.append((method, path, False, f"HTTP {e.code}: {msg}"))
        except Exception as e:
            self.results.append((method, path, False, str(e)))
        return None

    def _check(self, name: str, condition: bool, detail: str = ""):
        self.results.append(("CHK", name, bool(condition), detail if not condition else ""))

    def _first_id(self, rows):
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, dict) and row.get("id"):
                    return row["id"]
        return None

    def run(self):
        login = self._call("POST", "/auth/login", {"username": "admin", "password": "Admin@123456"})
        if not login:
            return
        self.token = login["access_token"]

        buildings = self._call("GET", "/assets/buildings") or []
        if buildings:
            building_id = buildings[0]["id"]
        else:
            building_id = self._call("POST", "/assets/buildings", {"name": "B栋", "code": f"B{datetime.now().strftime('%H%M%S')}"})["id"]
        floor = self._call("POST", "/assets/floors", {"building_id": building_id, "floor_no": 2, "name": "2层"})
        room = self._call("POST", "/assets/rooms", {"building_id": building_id, "floor_id": floor["id"], "room_no": f"2{datetime.now().strftime('%M%S')}", "room_type": "double"})
        bed = self._call("POST", "/assets/beds", {"room_id": room["id"], "bed_no": "1"})
        self._call("GET", "/assets/floors")
        self._call("GET", "/assets/rooms")
        self._call("GET", "/assets/beds")
        self._call("PATCH", f"/assets/beds/{bed['id']}/status", {"status": "reserved"})
        self._call("PATCH", f"/assets/beds/{bed['id']}/status", {"status": "vacant"})

        lead = self._call("POST", "/elders/leads", {"name": "回归老人", "phone": "13900000000", "source_channel": "script", "notes": "api"})
        elder = self._call("POST", "/elders", {"lead_id": lead["id"], "elder_no": f"ELD-{datetime.now().strftime('%H%M%S')}", "name": "回归老人", "gender": "male", "care_level": "L2"})
        self._call("GET", "/elders/leads")
        self._call("GET", "/elders")
        self._call("POST", f"/elders/{elder['id']}/admit", {"building_id": building_id, "floor_id": floor["id"], "room_id": room["id"], "bed_id": bed["id"], "admission_date": str(date.today())})

        item = self._call("POST", "/care/items", {"name": "洗浴", "category": "care", "unit_price": 88, "duration_min": 45})
        pkg = self._call("POST", "/care/packages", {"name": "日常护理包", "period": "daily"})
        self._call("POST", "/care/package-items", {"package_id": pkg["id"], "item_id": item["id"], "quantity": 1})
        elder_pkg = self._call("POST", "/care/elder-packages", {"elder_id": elder["id"], "package_id": pkg["id"], "start_date": str(date.today())})
        self._call("PATCH", f"/care/items/{item['id']}/status", {"status": "disabled"})
        self._call("PATCH", f"/care/items/{item['id']}/status", {"status": "active"})
        self._call("GET", "/care/items")
        self._call("GET", "/care/packages")
        self._call("GET", "/care/caregivers")
        assignment = self._call("POST", "/care/package-assignments", {"package_id": pkg["id"], "caregiver_id": login["user_id"], "start_date": str(date.today()), "months": 6})
        self._check("care.assignment_created", bool(assignment and assignment.get("id")), f"assignment={assignment}")
        tasks = self._call("POST", "/care/tasks/generate", {"elder_package_id": elder_pkg["id"], "scheduled_at": datetime.now(timezone.utc).isoformat()}) or []
        listed_tasks = self._call("GET", "/care/tasks") or []
        task_id = self._first_id(tasks) or self._first_id(listed_tasks)
        self._check("care.task_generated", bool(task_id), f"tasks={tasks}")
        if task_id:
            self._call("POST", f"/care/tasks/{task_id}/scan-in", {"qr_value": bed["qr_code"]})
            board = self._call("GET", "/care/tasks/board") or []
            self._check("care.board_in_progress", len(board) >= 1, f"board={board}")
            self._call("POST", f"/care/tasks/{task_id}/scan-out", {"qr_value": bed["qr_code"]})
            self._call("POST", f"/care/tasks/{task_id}/supervise", {"score": 96})
            self._call("POST", f"/care/tasks/{task_id}/issues", {"photo_urls": ["https://example.com/check.jpg"], "description": "地面湿滑", "report_to_dean": True})
            self._call("POST", f"/care/tasks/{task_id}/dean-review", {"approved": True, "note": "核查通过", "deduction_score": 25})
            perf = self._call("GET", f"/care/caregivers/{login['user_id']}/performance") or {}
            self._check("care.performance_deducted", perf.get("score", 100) <= 75, f"perf={perf}")
            self._check("care.rotation_suggestion", bool(perf.get("rotation_suggestion")), f"perf={perf}")

        self._call("POST", "/care/tasks/round", {"elder_id": elder["id"], "item_id": item["id"], "round_type": "nursing_round", "scheduled_at": datetime.now(timezone.utc).isoformat()})
        self._call("POST", "/care/tasks/dispatch", {"elder_package_id": elder_pkg["id"], "dispatch_type": "emergency", "frequency": "day", "custom_times": 1, "start_at": datetime.now(timezone.utc).isoformat()})
        self._call("POST", "/care/tasks/dispatch", {"elder_package_id": elder_pkg["id"], "dispatch_type": "periodic", "frequency": "custom", "custom_times": 2, "start_at": datetime.now(timezone.utc).isoformat()})

        order = self._call("POST", "/m4-medication/orders", {"elder_id": elder["id"], "drug_name": "阿司匹林", "dosage": "100mg", "frequency": "qd", "start_date": str(date.today())})
        self._call("POST", "/m4-medication/executions", {"order_id": order["id"], "result": "done", "note": "按时执行"})
        self._call("GET", "/m4-medication/orders")
        self._call("GET", "/m4-medication/executions")

        plan = self._call("POST", "/m5-meal/plans", {"name": "高蛋白菜谱", "plan_date": str(date.today()), "meal_type": "lunch", "nutrition_tag": "high_protein", "note": "少盐"})
        self._call("POST", "/m5-meal/orders", {"elder_id": elder["id"], "plan_id": plan["id"]})
        self._call("GET", "/m5-meal/plans")
        self._call("GET", "/m5-meal/orders")

        self._call("POST", "/m6-health/vitals", {"elder_id": elder["id"], "temperature": 36.6, "systolic": 122, "diastolic": 79, "pulse": 72})
        self._call("POST", "/m6-health/assessments", {"elder_id": elder["id"], "assessed_on": str(date.today()), "adl_score": 80, "mmse_score": 28, "risk_level": "low"})
        self._call("GET", "/m6-health/vitals")
        self._call("GET", "/m6-health/assessments")

        self._call("POST", "/m7-billing/items", {"elder_id": elder["id"], "item_name": "手工补费", "amount": 19.9, "charged_on": str(date.today())})
        self._call("POST", "/m7-billing/invoices", {"elder_id": elder["id"], "period_month": date.today().strftime('%Y-%m'), "total_amount": 200})
        self._call("GET", "/m7-billing/items")
        self._call("GET", "/m7-billing/invoices")

        shift = self._call("POST", "/oa1-shift/templates", {"name": "早班", "start_time": "08:00", "end_time": "16:00"})
        self._call("POST", "/oa1-shift/assignments", {"shift_id": shift["id"], "user_id": login["user_id"], "duty_date": str(date.today())})
        self._call("GET", "/oa1-shift/templates")
        self._call("GET", "/oa1-shift/assignments")

        self._call("POST", "/oa2-approval/requests", {"module": "care", "biz_id": elder["id"], "applicant_id": login["user_id"], "note": "请审批"})
        self._call("GET", "/oa2-approval/requests")
        self._call("POST", "/oa3-notification/messages", {"title": "交班", "content": "请查看", "channel": "in_app", "receiver_scope": "all"})
        self._call("GET", "/oa3-notification/messages")
        course = self._call("POST", "/oa4-training/courses", {"title": "跌倒预防", "category": "safety", "required_score": 80})
        self._call("POST", "/oa4-training/records", {"course_id": course["id"], "user_id": login["user_id"], "score": 92})
        self._call("GET", "/oa4-training/courses")
        self._call("GET", "/oa4-training/records")

        self._call("POST", "/b1-miniapp/requests", {"elder_id": elder["id"], "request_type": "repair", "content": "呼叫器异常"})
        self._call("GET", "/b1-miniapp/requests")
        family = self._call("POST", "/b2-family/accounts", {"elder_id": elder["id"], "name": "家属A", "phone": "13700000000", "relation": "子女"})
        self._call("POST", "/b2-family/visits", {"family_id": family["id"], "visit_date": str(date.today())})
        self._call("GET", "/b2-family/accounts")
        self._call("GET", "/b2-family/visits")
        family_overview = self._call("GET", f"/b2-family/elders/{elder['id']}/overview") or {}
        family_catalog = self._call("GET", "/b2-family/services/catalog") or {}
        self._check("family.overview_ready", isinstance(family_overview, dict) and bool(family_overview.get("elder")), f"overview={family_overview}")
        self._check("family.catalog_ready", isinstance(family_catalog, dict) and len(family_catalog.get("packages", [])) > 0, f"catalog={family_catalog}")
        if family_catalog.get("packages"):
            self._call("POST", "/b2-family/services/order", {"elder_id": elder["id"], "package_id": family_catalog["packages"][0]["id"]})

        family_bills = self._call("GET", f"/b2-family/elders/{elder['id']}/bills") or []
        family_records = self._call("GET", f"/b2-family/elders/{elder['id']}/care-records") or []
        self._check("linkage.auto_billing_visible_to_family", len(family_bills) > 0, f"bills={family_bills}")
        self._check("linkage.care_record_visible_to_family", len(family_records) > 0, f"records={family_records}")
        self._call("POST", "/b2-family/surveys", {"elder_id": elder["id"], "family_id": family["id"], "score": 5, "comment": "满意"})
        surveys = self._call("GET", f"/b2-family/surveys?elder_id={elder['id']}") or []
        self._check("linkage.family_survey_recorded", len(surveys) > 0, f"surveys={surveys}")

        self._call("POST", "/b3-dashboard/metrics", {"metric_date": str(date.today()), "occupancy_rate": 86.5, "revenue": 1000, "alerts": 2})
        self._call("GET", "/b3-dashboard/metrics")
        summary = self._call("GET", "/b3-dashboard/performance-summary") or {}
        self._check("linkage.performance_summary", isinstance(summary, dict) and len(summary) > 0, f"summary={summary}")

        self._call("GET", f"/elders/{elder['id']}/logs")
        self._call("POST", f"/elders/{elder['id']}/discharge", {"discharge_date": str(date.today()), "note": "脚本退院"})


def main():
    c = Client()
    c.run()
    ok_count = sum(1 for _, _, ok, _ in c.results if ok)
    fail = [x for x in c.results if not x[2]]
    print("=" * 88)
    print(f"API回归结果: total={len(c.results)} pass={ok_count} fail={len(fail)}")
    for method, path, ok, msg in c.results:
        print(f"[{ 'PASS' if ok else 'FAIL' }] {method:5s} {path} {msg}")
    print("=" * 88)
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
