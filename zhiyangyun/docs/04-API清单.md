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
- M4 用药：`/m4-medication/*`
- M5 膳食：`/m5-meal/*`
- M6 健康：`/m6-health/*`
- M7 财务：`/m7-billing/*`

## A2
- OA1 排班：`/oa1-shift/*`
- OA2 审批：`/oa2-approval/*`
- OA3 通知：`/oa3-notification/*`
- OA4 培训：`/oa4-training/*`

## B
- B1：`/b1-miniapp/*`
- B2：`/b2-family/*`
  - 新增：
    - `GET /b2-family/elders/{elder_id}/overview`
    - `GET /b2-family/services/catalog`
    - `POST /b2-family/services/order`
- B3：`/b3-dashboard/*`

> 建议：将 `scripts/api_regression.py` 作为清单事实来源，后续可自动生成 OpenAPI 对照文档。
