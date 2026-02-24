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
建档 → 入院 → 床位绑定（库存）→ 护理服务项/套餐（商城）→ 护理任务（订单）→ 护理扫码完成自动扣费并计入账单/发票（余额）→ **M4 用药执行自动计费并汇总发票** → 家属查看账单/护理记录 → 家属问卷评价 → 绩效统计 → 看板展示

## 2026-02 护理治理升级（本次新增）
1. **护理项目中心**：独立护理项目可新增/删除/启停；项目包支持默认半年配置。
2. **项目包分配到护理员**：`/care/package-assignments` 记录责任护理员、生效周期（默认 6 个月）。
3. **任务精确计时**：扫码打卡精确到秒，记录开始/结束/总秒数；任务看板 `/care/tasks/board` 展示“谁在做什么+耗时”。
4. **查房任务**：护理部部长/生活管理员/行政可新增护理查房、行政查房（`/care/tasks/round`）。
5. **规范检查留档**：任务支持上传照片URL与问题描述，并可上报院长（`/care/tasks/{id}/issues`）。
6. **院长审核与绩效扣分**：护理员绩效初始100；院长审核通过后扣分；<80 自动生成“下月调岗建议”。
7. **紧急任务与周期下发**：支持紧急一键下发、按天/月/季度/年/自定义次数批量下发（`/care/tasks/dispatch`）。

### 关键联动点
- M1 新增床位运营视图：`GET /assets/occupancy-summary`（入住率、空床、异常床位）
- M1 新增一键对账修复：`POST /assets/beds/reconcile`（自动修正“床位状态 vs 在住长者绑定”不一致）
- M1 限制手工把床位设为 occupied：需先由 M2 入院/转床绑定在住长者
- M2 新增全周期经营看板：线索量、在院人数、入院转化率
- M2 新增床位联动巡检：`GET /elders/audit/bed-sync`，主动检查在院长者与 M1 床位状态一致性
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
- `GET /api/v1/b2-family/elders/{elder_id}/overview`（新增：家属长者总览）
- `GET /api/v1/b2-family/services/catalog`（新增：家属服务目录）
- `POST /api/v1/b2-family/services/order`（新增：家属服务增购）
- `GET /api/v1/b2-family/surveys?elder_id=...`
- `POST /api/v1/b2-family/surveys`
- `GET /api/v1/b3-dashboard/performance-summary`
- `PATCH /api/v1/care/items/{id}/status`
- `DELETE /api/v1/care/items/{id}`
- `POST /api/v1/care/package-assignments`
- `GET /api/v1/care/caregivers`
- `GET /api/v1/care/tasks/board`
- `POST /api/v1/care/tasks/round`
- `POST /api/v1/care/tasks/{id}/issues`
- `POST /api/v1/care/tasks/{id}/dean-review`
- `POST /api/v1/care/tasks/dispatch`
- `GET /api/v1/care/caregivers/{id}/performance`
- `GET /api/v1/assets/occupancy-summary`
- `POST /api/v1/assets/beds/reconcile`
- `GET /api/v1/elders/overview/summary`
- `GET /api/v1/elders/audit/bed-sync`
- `GET /api/v1/care/governance-summary`
- `GET /api/v1/m7-billing/items?page=...&page_size=...&keyword=...&status=...`
- `GET /api/v1/m7-billing/invoices?page=...&page_size=...&keyword=...&status=...`
- `POST /api/v1/m7-billing/invoices/generate`
- `POST /api/v1/m7-billing/invoices/{id}/writeoff`
- `POST /api/v1/m7-billing/invoices/{id}/exception`
- `GET /api/v1/m7-billing/invoices/{id}/events`
- `GET /api/v1/oa1-shift/templates?page=...&page_size=...&keyword=...&status=...`
- `GET /api/v1/oa1-shift/assignments?page=...&page_size=...&keyword=...&status=...`
- `POST /api/v1/oa1-shift/assignments/{id}/status`

## 前端联调入口
- `M2 长者全周期管理`：建档+入院/转床/退院
- `M3 服务与护理标准化`：任务扫码开始/完成、监督评分（扫码值会自动取长者床位二维码）
- `A1-M7 费用管理`：收费业务闭环（账单明细分页检索、发票生成、核销、异常处理、事件流水）
- `A2-OA1 排班管理`：模板/排班双列表分页检索、姓名化展示、状态流转操作
- `B2 家属门户`：查看账单、护理记录、提交问卷评价
- `B3 运营看板`：展示实时绩效汇总 + 历史指标

## 开发文档（docs）
- `docs/01-功能遗漏审计.md`
- `docs/02-架构说明.md`
- `docs/03-数据模型字典.md`
- `docs/04-API清单.md`
- `docs/05-业务流程时序.md`
- `docs/06-权限矩阵.md`
- `docs/07-部署运维.md`
- `docs/08-测试与验收手册.md`
- `docs/09-变更日志.md`
- `docs/10-OA1-自动准备清单.md`

## 商城+库存（本次优先补齐）
### 能力清单
1. **商品/SPU-SKU 管理**
   - 分类：`GET/POST /api/v1/shop/categories`
   - SPU：`GET/POST /api/v1/shop/spu`，上下架：`PATCH /api/v1/shop/spu/{id}/status`
   - SKU：`GET/POST /api/v1/shop/sku`，支持中文字段、分类/名称展示
2. **库存台账**
   - 入库：`POST /api/v1/shop/inventory/in`
   - 出库：`POST /api/v1/shop/inventory/out`
   - 盘点：`POST /api/v1/shop/inventory/check`
   - 台账：`GET /api/v1/shop/inventory/ledger`
   - 预警：`GET /api/v1/shop/inventory/warnings`
3. **订单流程**
   - 下单：`POST /api/v1/shop/orders`
   - 支付：`POST /api/v1/shop/orders/{id}/pay`
   - 取消：`POST /api/v1/shop/orders/{id}/cancel`
   - 退款：`POST /api/v1/shop/orders/{id}/refund`
   - 完成：`POST /api/v1/shop/orders/{id}/complete`
4. **余额账单联动**
   - 订单支付自动记账（扣费流水）
   - 订单退款自动记账（退款流水）
   - 查询：`GET /api/v1/shop/elders/{elder_id}/account-ledger`
5. **库存预占/防超卖/失败回滚**
   - 下单时先预占库存（`reserve` 台账 + reservation）
   - 库存不足会拒绝下单（防超卖）
   - 取消订单自动释放预占
6. **家属端可见**
   - 家属可查订单：`GET /api/v1/b2-family/elders/{elder_id}/orders`
   - 家属可查余额变动：`GET /api/v1/b2-family/elders/{elder_id}/balance-changes`
7. **前端体验**
   - 新增 `A1-M8 商城+库存` 页面（`/shop`）
   - 列表分页/搜索
   - SKU 自动联想
   - 列表展示中文名与长者姓名（替代纯 ID）

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

覆盖范围：
- 已实现全部业务接口（登录、资产、长者、M3~M7、OA1~OA4、B1~B3）
- 关键联动校验（脚本内 `CHK`）：
  - 护理任务成功生成（兼容 `/care/tasks/generate` 返回结构）
  - 护理扫码完成后自动扣费，家属账单可见
  - 护理记录写入并家属可见
  - 家属问卷提交后可查询
  - 看板绩效汇总接口可读

## UI / 功能验收清单
### 一、统一设计系统
- [ ] 页面统一使用 `page-title + zy-card` 结构，主题蓝 `#2f6bff`
- [ ] 表单控件间距、按钮操作区、空态提示样式统一
- [ ] 状态统一用标签色：成功/进行中/失败/默认
- [ ] 关键页面均有流程提示（Alert）

### 二、可理解 / 可操作 / 可视化
- [ ] 所有 A1-M1~M7、A2-OA1~OA4、B1~B3 页面具备中文化标题/说明
- [ ] 列表页支持至少一种筛选（关键字/状态）
- [ ] 列表页具备分页能力（通用模块通过 `ModuleCrudPage`）
- [ ] 通用模块支持详情抽屉查看完整字段
- [ ] 表单必填校验提示中文化

### 三、联动体验（重点）
- [ ] M1 床位准备后，M2 可执行入院/转床/退院
- [ ] M2 在院长者可在 M3 执行任务生成与扫码流程
- [ ] M3 完成任务后，M7 可查看自动扣费结果
- [ ] M4 用药执行后，M7 可查看“用药执行”自动计费条目
- [ ] M5 膳食下发后，M7 可查看“膳食供应”自动计费条目
- [ ] M6 体征异常自动生成“健康随访”任务并发送 OA3 告警，评估记录支持闭环
- [ ] B2 可查看账单、护理记录并提交问卷
- [ ] B3 可展示实时绩效汇总与历史补录数据

### 四、错误处理友好化
- [ ] 前端拦截器统一解析 `message/detail/trace_id`
- [ ] 401 自动清理登录态并跳转登录
- [ ] 404/500/超时有中文提示
- [ ] 页面级提交失败给出可理解提示

### 五、构建与联调
- [ ] `cd web && npm run build` 通过
- [ ] 关键链路手工验证：M1→M2→M3→M7→B2→B3

## 最终验收步骤（可直接照抄）
```bash
# 1) 全量启动
docker compose up --build -d

# 2) 迁移 + 种子
cd backend && alembic upgrade head && cd ..
docker compose run --rm seed

# 3) 关键 API 回归（含全链路 CHK）
python3 scripts/api_regression.py

# 4) 前端构建
cd web && npm install && npm run build && cd ..

# 5) 关键接口冒烟
curl -s http://localhost:8000/health
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"Admin@123456"}'
```

## 故障排查
- `api_regression.py` 在任务生成处报 `KeyError: 'id'`
  - 现已修复后端 `CareService.generate_tasks`：提交后逐条 `db.refresh(task)`，确保返回结构包含 `id`。
  - 脚本也增加兼容：优先使用 generate 返回值，必要时回退到 `/care/tasks` 列表取 `id`。

- 前端构建报 `vue-tsc: command not found`
  - 先执行 `cd web && npm install` 再 `npm run build`。

- 首次启动接口 401/空数据
  - 确认已执行 `docker compose run --rm seed`，并使用默认账号 `admin / Admin@123456`。

- 看板无数据
  - 先跑一轮 `python3 scripts/api_regression.py`，脚本会自动生成联动业务数据。

## 迁移说明
本次新增迁移：
- `2026021115_linkage_enhance.py`
  - `family_care_records`
  - `family_surveys`
- `2026021117_shop_inventory.py`
  - 商城分类/SPU/SKU
  - 库存台账与预占
  - 订单主子表
  - 余额与流水账本
- `2026021118_m6_health_upgrade.py`
  - 生命体征异常级别/异常原因/随访任务关联字段
  - 健康评估闭环状态、闭环时间、闭环备注字段
- `2026021119_m7_billing_events.py`
  - 新增收费事件表 `billing_events`（生成/核销/异常处理全程留痕）
- `2026021120_oa1_upgrade.py`
  - OA1 班次模板新增 `status` 字段，排班状态统一收敛到 `draft` 起始态

如本地已启动旧库，请先执行：
```bash
cd backend
alembic upgrade head
```
