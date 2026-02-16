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
        occupancy = self._call("GET", "/assets/occupancy-summary") or {}
        self._check("m1.occupancy_summary_ready", isinstance(occupancy, dict) and "occupancy_rate" in occupancy, f"occupancy={occupancy}")
        reconcile = self._call("POST", "/assets/beds/reconcile") or {}
        self._check("m1.reconcile_api_ready", isinstance(reconcile, dict) and "fixed_count" in reconcile, f"reconcile={reconcile}")

        lead = self._call("POST", "/elders/leads", {"name": "回归老人", "phone": "13900000000", "source_channel": "script", "notes": "api"})
        elder = self._call("POST", "/elders", {"lead_id": lead["id"], "elder_no": f"ELD-{datetime.now().strftime('%H%M%S')}", "name": "回归老人", "gender": "male", "care_level": "L2"})
        self._call("GET", "/elders/leads")
        self._call("GET", "/elders")
        elder_overview = self._call("GET", "/elders/overview/summary") or {}
        self._check("m2.overview_ready", isinstance(elder_overview, dict) and "admission_conversion_rate" in elder_overview, f"overview={elder_overview}")
        self._call("POST", f"/elders/{elder['id']}/admit", {"building_id": building_id, "floor_id": floor["id"], "room_id": room["id"], "bed_id": bed["id"], "admission_date": str(date.today())})
        bed_sync = self._call("GET", "/elders/audit/bed-sync") or {}
        self._check("m2.bed_sync_audit_ready", isinstance(bed_sync, dict) and "issue_count" in bed_sync, f"audit={bed_sync}")

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

        governance = self._call("GET", "/care/governance-summary") or {}
        self._check("m3.governance_summary_ready", isinstance(governance, dict) and "overdue_count" in governance, f"governance={governance}")

        self._call("POST", "/care/tasks/round", {"elder_id": elder["id"], "item_id": item["id"], "round_type": "nursing_round", "scheduled_at": datetime.now(timezone.utc).isoformat()})
        self._call("POST", "/care/tasks/dispatch", {"elder_package_id": elder_pkg["id"], "dispatch_type": "emergency", "frequency": "day", "custom_times": 1, "start_at": datetime.now(timezone.utc).isoformat()})
        self._call("POST", "/care/tasks/dispatch", {"elder_package_id": elder_pkg["id"], "dispatch_type": "periodic", "frequency": "custom", "custom_times": 2, "start_at": datetime.now(timezone.utc).isoformat()})

        order = self._call("POST", "/m4-medication/orders", {"elder_id": elder["id"], "drug_name": "阿司匹林", "dosage": "100mg", "frequency": "qd", "start_date": str(date.today())})
        suggest = self._call("GET", f"/m4-medication/elders/suggest?keyword={elder['name']}") or []
        self._check("m4.elder_autocomplete_ready", len(suggest) > 0, f"suggest={suggest}")
        paged_orders = self._call("GET", "/m4-medication/orders?page=1&page_size=5&keyword=阿司") or {}
        self._check("m4.order_pagination_ready", isinstance(paged_orders, dict) and "items" in paged_orders and "total" in paged_orders, f"paged={paged_orders}")
        self._check("m4.order_name_present", bool((paged_orders.get("items") or [{}])[0].get("elder_name")), f"paged={paged_orders}")
        self._call("POST", "/m4-medication/executions", {"order_id": order["id"], "result": "done", "note": "按时执行"})
        m4_execs = self._call("GET", "/m4-medication/executions") or []
        self._check("m4.execution_name_present", bool(m4_execs and m4_execs[0].get("elder_name")), f"execs={m4_execs}")
        m7_items = self._call("GET", "/m7-billing/items") or []
        self._check("m4.execution_auto_billing", any((x.get("item_name") or "").startswith("用药执行") for x in m7_items), f"items={m7_items}")

        plan = self._call("POST", "/m5-meal/plans", {"name": "高蛋白菜谱", "plan_date": str(date.today()), "meal_type": "lunch", "nutrition_tag": "high_protein", "note": "少盐"})
        m5_suggest = self._call("GET", f"/m5-meal/elders/suggest?keyword={elder['name']}") or []
        self._check("m5.elder_autocomplete_ready", len(m5_suggest) > 0, f"suggest={m5_suggest}")
        m5_paged_plan = self._call("GET", "/m5-meal/plans?page=1&page_size=5&keyword=高蛋白") or {}
        self._check("m5.plan_pagination_ready", isinstance(m5_paged_plan, dict) and "items" in m5_paged_plan and "total" in m5_paged_plan, f"plan={m5_paged_plan}")
        self._call("POST", "/m5-meal/orders", {"elder_id": elder["id"], "plan_id": plan["id"]})
        m5_orders = self._call("GET", "/m5-meal/orders?page=1&page_size=5") or {}
        m5_order_items = m5_orders.get("items", []) if isinstance(m5_orders, dict) else (m5_orders or [])
        first_order = (m5_order_items or [{}])[0]
        self._check("m5.order_name_present", bool(first_order.get("elder_name") and first_order.get("plan_name")), f"orders={m5_orders}")
        m7_items_after_m5 = self._call("GET", "/m7-billing/items") or []
        self._check("m5.order_auto_billing", any((x.get("item_name") or "").startswith("膳食供应") for x in m7_items_after_m5), f"items={m7_items_after_m5}")

        self._call("POST", "/m6-health/vitals", {"elder_id": elder["id"], "temperature": 39.1, "systolic": 186, "diastolic": 113, "pulse": 128})
        m6_vitals = self._call("GET", "/m6-health/vitals?page=1&page_size=5&keyword=回归") or {}
        m6_vital_items = m6_vitals.get("items", []) if isinstance(m6_vitals, dict) else []
        self._check("m6.vital_pagination_ready", isinstance(m6_vitals, dict) and "items" in m6_vitals and "total" in m6_vitals, f"vitals={m6_vitals}")
        self._check("m6.vital_name_present", bool(m6_vital_items and m6_vital_items[0].get("elder_name")), f"vitals={m6_vitals}")
        self._check("m6.vital_alert_rule_ready", bool(m6_vital_items and m6_vital_items[0].get("abnormal_level") in ["warning", "critical"]), f"vitals={m6_vitals}")

        m6_high = self._call("POST", "/m6-health/assessments", {"elder_id": elder["id"], "assessed_on": str(date.today()), "adl_score": 35, "mmse_score": 16, "risk_level": "high"})
        m6_assessments = self._call("GET", "/m6-health/assessments?page=1&page_size=5&keyword=回归") or {}
        m6_assessment_items = m6_assessments.get("items", []) if isinstance(m6_assessments, dict) else []
        self._check("m6.assessment_pagination_ready", isinstance(m6_assessments, dict) and "items" in m6_assessments and "total" in m6_assessments, f"assessments={m6_assessments}")
        self._check("m6.assessment_name_present", bool(m6_assessment_items and m6_assessment_items[0].get("elder_name")), f"assessments={m6_assessments}")
        self._check("m6.assessment_linkage_task_ready", bool(m6_high and m6_high.get("followup_task_id")), f"assessment={m6_high}")
        if m6_high and m6_high.get("id"):
            self._call("POST", f"/m6-health/assessments/{m6_high['id']}/close", {"note": "回归闭环"})
            m6_closed = self._call("GET", "/m6-health/assessments?page=1&page_size=5&status=closed") or {}
            self._check("m6.assessment_closed_loop_ready", isinstance(m6_closed, dict) and len(m6_closed.get("items", [])) > 0, f"closed={m6_closed}")

        self._call("POST", "/m7-billing/items", {"elder_id": elder["id"], "item_name": "手工补费", "amount": 19.9, "charged_on": str(date.today())})
        m7_paged_items = self._call("GET", "/m7-billing/items?page=1&page_size=10&keyword=回归&status=unpaid") or {}
        self._check("m7.items_pagination_ready", isinstance(m7_paged_items, dict) and "items" in m7_paged_items and "total" in m7_paged_items, f"items={m7_paged_items}")
        first_m7_item = (m7_paged_items.get("items") or [{}])[0] if isinstance(m7_paged_items, dict) else {}
        self._check("m7.items_name_present", bool(first_m7_item.get("elder_name") and first_m7_item.get("elder_no")), f"items={m7_paged_items}")

        period = date.today().strftime('%Y-%m')
        m7_generated = self._call("POST", "/m7-billing/invoices/generate", {"elder_id": elder["id"], "period_month": period}) or {}
        self._check("m7.invoice_generated", bool(m7_generated.get("id")), f"invoice={m7_generated}")
        m7_writeoff = self._call("POST", f"/m7-billing/invoices/{m7_generated.get('id')}/writeoff", {"amount": 10, "note": "回归部分核销"}) or {}
        self._check("m7.invoice_writeoff_partial", m7_writeoff.get("status") == "partial", f"writeoff={m7_writeoff}")
        m7_overdue = self._call("POST", f"/m7-billing/invoices/{m7_generated.get('id')}/exception", {"action": "mark_overdue", "note": "回归逾期"}) or {}
        self._check("m7.invoice_exception_overdue", m7_overdue.get("status") == "overdue", f"overdue={m7_overdue}")
        m7_reopen = self._call("POST", f"/m7-billing/invoices/{m7_generated.get('id')}/exception", {"action": "reopen", "note": "回归重开"}) or {}
        self._check("m7.invoice_status_reopen", m7_reopen.get("status") in ["open", "partial"], f"reopen={m7_reopen}")
        m7_events = self._call("GET", f"/m7-billing/invoices/{m7_generated.get('id')}/events") or []
        self._check("m7.invoice_event_trace_ready", len(m7_events) >= 3, f"events={m7_events}")

        m7_paged_invoices = self._call("GET", f"/m7-billing/invoices?page=1&page_size=10&period_month={period}") or {}
        self._check("m7.invoice_pagination_ready", isinstance(m7_paged_invoices, dict) and "items" in m7_paged_invoices and "total" in m7_paged_invoices, f"invoices={m7_paged_invoices}")
        first_invoice = (m7_paged_invoices.get("items") or [{}])[0] if isinstance(m7_paged_invoices, dict) else {}
        self._check("m7.invoice_name_present", bool(first_invoice.get("elder_name") and first_invoice.get("unpaid_amount") is not None), f"invoices={m7_paged_invoices}")

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

        cat = self._call("POST", "/shop/categories", {"name_zh": "护理用品", "code": f"CAT{datetime.now().strftime('%H%M%S')}"})
        spu = self._call("POST", "/shop/spu", {"category_id": cat["id"], "name_zh": "护理湿巾", "subtitle_zh": "加厚款", "description_zh": "无酒精"}) if cat else None
        if spu:
            self._call("PATCH", f"/shop/spu/{spu['id']}/status", {"status": "on_shelf"})
        sku = self._call("POST", "/shop/sku", {"spu_id": spu["id"], "sku_name_zh": "护理湿巾-80抽", "sku_code": f"SKU{datetime.now().strftime('%H%M%S')}", "sale_price": 19.9, "warning_stock": 3, "available_stock": 8}) if spu else None
        if sku:
            self._call("POST", "/shop/inventory/in", {"sku_id": sku["id"], "quantity": 2, "remark": "回归补货"})
            self._call("POST", "/shop/inventory/out", {"sku_id": sku["id"], "quantity": 1, "remark": "回归出库"})
            self._call("POST", "/shop/inventory/check", {"sku_id": sku["id"], "actual_stock": 6, "remark": "回归盘点"})
        inv_ledger = self._call("GET", "/shop/inventory/ledger?page=1&page_size=10") or {}
        inv_warn = self._call("GET", "/shop/inventory/warnings") or []
        self._check("shop.inventory_ledger_ready", isinstance(inv_ledger, dict) and len(inv_ledger.get("items", [])) > 0, f"ledger={inv_ledger}")
        self._check("shop.inventory_warning_ready", isinstance(inv_warn, list), f"warn={inv_warn}")
        sku_suggest = self._call("GET", "/shop/sku/suggest?keyword=湿巾") or []
        self._check("shop.sku_autocomplete_ready", len(sku_suggest) > 0, f"suggest={sku_suggest}")

        order_created = self._call("POST", "/shop/orders", {"elder_id": elder["id"], "items": [{"sku_id": sku["id"], "quantity": 2}]}) if sku else None
        self._check("shop.order_created", bool(order_created and order_created.get("id")), f"order={order_created}")
        if order_created:
            self._call("POST", f"/shop/orders/{order_created['id']}/pay")
            self._call("POST", f"/shop/orders/{order_created['id']}/complete")
            self._call("POST", f"/shop/orders/{order_created['id']}/refund", {"reason": "回归退款"})
        order_cancel = self._call("POST", "/shop/orders", {"elder_id": elder["id"], "items": [{"sku_id": sku["id"], "quantity": 1}]}) if sku else None
        if order_cancel:
            self._call("POST", f"/shop/orders/{order_cancel['id']}/cancel", {"reason": "回归取消"})

        shop_orders = self._call("GET", "/shop/orders?page=1&page_size=10&keyword=回归") or {}
        self._check("shop.order_pagination_name_ready", isinstance(shop_orders, dict) and bool((shop_orders.get("items") or [{}])[0].get("elder_name")), f"orders={shop_orders}")
        account_ledger = self._call("GET", f"/shop/elders/{elder['id']}/account-ledger") or []
        self._check("shop.account_ledger_ready", len(account_ledger) > 0, f"ledger={account_ledger}")

        family_orders = self._call("GET", f"/b2-family/elders/{elder['id']}/orders") or []
        family_balance = self._call("GET", f"/b2-family/elders/{elder['id']}/balance-changes") or []
        self._check("family.shop_orders_visible", len(family_orders) > 0, f"orders={family_orders}")
        self._check("family.balance_changes_visible", len(family_balance) > 0, f"balance={family_balance}")

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
