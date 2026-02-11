# 智慧养老平台（跨模块联动版）

## 一键启动
```bash
docker compose up --build -d
# 首次启动或模型变更后执行
cd backend && alembic upgrade head && cd ..
docker compose run --rm seed
```

- API: http://localhost:8000/docs
- Web: http://localhost:5173
- 默认管理员：admin / Admin@123456

## 本次补齐的跨模块主链路
建档 → 入院 → 床位绑定 → 护理任务生成 → 护理扫码完成自动扣费 → 家属查看账单/护理记录 → 家属问卷评价 → 绩效统计 → 看板展示

### 关键联动点
- M2 入院/转床/退院增加状态机约束（仅 assessed/discharged 可入院；仅 admitted 可转床/退院）
- M3 扫码校验修复：扫码值必须匹配长者当前床位 `bed.qr_code`
- M3 任务状态机约束：`pending -> in_progress -> completed`
- M3 任务完成自动联动：
  - 自动新增 M7 计费明细（BillingItem）
  - 自动滚动累计当月发票（BillingInvoice.total_amount）
  - 自动写入 B2 家属护理记录（FamilyCareRecord）
- B2 新增家属侧查询接口：账单、护理记录、问卷
- B3 新增绩效汇总接口：任务完成数、监督均分、家属满意度、今日营收、床位占用率

## API 路由概览
- A1: `/api/v1/m4-medication/*`, `/m5-meal/*`, `/m6-health/*`, `/m7-billing/*`
- A2: `/api/v1/oa1-shift/*`, `/oa2-approval/*`, `/oa3-notification/*`, `/oa4-training/*`
- B: `/api/v1/b1-miniapp/*`, `/b2-family/*`, `/b3-dashboard/*`

本次新增：
- `GET /api/v1/b2-family/elders/{elder_id}/bills`
- `GET /api/v1/b2-family/elders/{elder_id}/care-records`
- `GET /api/v1/b2-family/surveys?elder_id=...`
- `POST /api/v1/b2-family/surveys`
- `GET /api/v1/b3-dashboard/performance-summary`

## 前端联调入口
- `M2 长者全周期管理`：建档+入院/转床/退院
- `M3 服务与护理标准化`：任务扫码开始/完成、监督评分（扫码值会自动取长者床位二维码）
- `A1-M7 费用管理`：可见自动扣费后的明细与发票
- `B2 家属门户`：查看账单、护理记录、提交问卷评价
- `B3 运营看板`：展示实时绩效汇总 + 历史指标

## 自动化 API 回归
脚本位置：`scripts/api_regression.py`

执行：
```bash
python3 scripts/api_regression.py
# 或指定地址
python3 scripts/api_regression.py http://localhost:8000/api/v1
```

输出格式：
- 总计 `total/pass/fail`
- 每条接口 `PASS/FAIL + 方法 + 路径 + 错误信息`
- 任一失败返回非 0（可直接接 CI）

覆盖范围：已实现全部业务接口（登录、资产、长者、M3~M7、OA1~OA4、B1~B3、新增家属与看板接口）。

## 迁移说明
本次新增迁移：
- `2026021115_linkage_enhance.py`
  - `family_care_records`
  - `family_surveys`

如本地已启动旧库，请先执行：
```bash
cd backend
alembic upgrade head
```
