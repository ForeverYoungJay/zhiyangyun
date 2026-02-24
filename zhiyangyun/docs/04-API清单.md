# API 清单（按模块）

## 认证
- `POST /api/v1/auth/login`

## A1
- M1 资产：`/assets/*`
  - 新增：
    - `GET /assets/occupancy-summary`
    - `POST /assets/beds/reconcile`
- M2 长者：`/elders/*`
  - 新增：
    - `GET /elders/overview/summary`
    - `GET /elders/audit/bed-sync`
- M3 护理：`/care/*`
  - 新增：
    - `GET /care/governance-summary`
- M4 用药：`/m4-medication/*`
  - 新增：
    - `GET /m4-medication/elders/suggest?keyword=...&limit=...`
    - `GET /m4-medication/orders?page=...&page_size=...&keyword=...&status=...`
  - 联动：
    - `POST /m4-medication/executions` 成功后自动写入 M7 `billing_items` 并累计当月 `billing_invoices.total_amount`
- M5 膳食：`/m5-meal/*`
  - 新增：
    - `GET /m5-meal/elders/suggest?keyword=...&limit=...`
    - `GET /m5-meal/plans?page=...&page_size=...&keyword=...&meal_type=...`
    - `GET /m5-meal/orders?page=...&page_size=...&keyword=...`
  - 联动：
    - `POST /m5-meal/orders` 成功后自动写入 M7 `billing_items` 并累计当月 `billing_invoices.total_amount`
- M6 健康：`/m6-health/*`
  - 新增：
    - `GET /m6-health/elders/suggest?keyword=...&limit=...`
    - `GET /m6-health/vitals?page=...&page_size=...&keyword=...&abnormal_level=...`
    - `GET /m6-health/assessments?page=...&page_size=...&keyword=...&status=...`
    - `POST /m6-health/assessments/{id}/close`
  - 业务联动：
    - `POST /m6-health/vitals` 命中异常规则后自动创建健康随访任务（M3）并发送 OA3 告警
    - `POST /m6-health/assessments` 高风险时自动创建闭环任务并写入审批待办
- M7 财务：`/m7-billing/*`
  - 列表查询：
    - `GET /m7-billing/items?page=...&page_size=...&keyword=...&status=...&elder_id=...`
    - `GET /m7-billing/invoices?page=...&page_size=...&keyword=...&status=...&period_month=...`
  - 收费业务流：
    - `POST /m7-billing/invoices/generate`（按账单自动生成月度发票）
    - `POST /m7-billing/invoices/{id}/writeoff`（核销，支持部分/全额）
    - `POST /m7-billing/invoices/{id}/exception`（逾期/争议/豁免/重开）
    - `GET /m7-billing/invoices/{id}/events`（状态流转与操作留痕）

## A2
- OA1 排班：`/oa1-shift/*`
  - 列表查询：
    - `GET /oa1-shift/templates?page=...&page_size=...&keyword=...&status=...`
    - `GET /oa1-shift/assignments?page=...&page_size=...&keyword=...&status=...&shift_id=...&user_id=...&duty_date=...&start_date=...&end_date=...`
  - 业务规则：
    - `POST /oa1-shift/templates` 校验时间合法（开始时间 < 结束时间）与模板去重（同名同时间）
    - `POST /oa1-shift/assignments` 校验不可排过去日期，同人同日班次冲突自动拦截
  - 状态流转：
    - `POST /oa1-shift/assignments/{id}/status`（`publish/execute/mark_exception/reopen`）
    - 发布动作自动联动 OA2：生成 `module=oa1_shift` 审批待办（pending）
  - 姓名化字段：`user_name/display_name/username/shift_name`

- OA2 审批：`/oa2-approval/*`
  - 列表查询：
    - `GET /oa2-approval/requests?page=...&page_size=...&keyword=...&status=...&module=...`
  - 状态机与抄送：
    - `POST /oa2-approval/requests`（支持 `cc_user_ids[]`、`total_steps`）
    - `POST /oa2-approval/requests/{id}/action`（`approve/reject/cancel`）
    - `GET /oa2-approval/requests/{id}/logs`（审批轨迹）
  - 姓名化：`applicant_display_name/approver_display_name/cc_names[]`

- OA3 通知：`/oa3-notification/*`
  - 列表查询：
    - `GET /oa3-notification/messages?page=...&page_size=...&keyword=...&status=...&channel=...&strategy=...&receiver_scope=...`
  - 触达策略：
    - `POST /oa3-notification/messages`（支持 `strategy=immediate/queued`、`receiver_scope=all/single`、`target_user_id`）
    - `POST /oa3-notification/messages/{id}/action`（`deliver/retry/fail`，含状态机约束）
  - 姓名化：`target_name`

- OA4 培训：`/oa4-training/*`
  - 计划列表：
    - `GET /oa4-training/courses?page=...&page_size=...&keyword=...&status=...`
  - 签到/考核闭环：
    - `GET /oa4-training/records?page=...&page_size=...&keyword=...&status=...&course_id=...`
    - `POST /oa4-training/records`
    - `POST /oa4-training/records/{id}/action`（`sign_in/absent/assess`；考核前必须签到，及格线取课程 `required_score`）
    - `GET /oa4-training/courses/{id}/closure`
  - 名称化：`trainer_name/user_name/evaluator_name`

## B
- B1：`/b1-miniapp/*`
- B2：`/b2-family/*`
  - 新增：
    - `GET /b2-family/elders/{elder_id}/overview`
    - `GET /b2-family/services/catalog`
    - `POST /b2-family/services/order`
- B3：`/b3-dashboard/*`

> 建议：将 `scripts/api_regression.py` 作为清单事实来源，后续可自动生成 OpenAPI 对照文档。
