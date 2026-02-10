# 智慧养老平台（已覆盖 A1-M1~M7、A2-OA1~OA4、B1~B3 最小闭环）

## 一键启动
```bash
docker compose up --build -d
# 首次启动后执行种子数据
docker compose run --rm seed
```

- API: http://localhost:8000/docs
- Web: http://localhost:5173
- 默认管理员：admin / Admin@123456

## 本阶段能力
- 多租户 tenant_id 隔离（业务查询均按 token 中 tenant_id）
- JWT 登录鉴权
- 统一返回格式：`{success, message, data}`

### A1 模块
- M1 资产与房间管理
- M2 长者全周期管理
- M3 服务与护理标准化
- M4 用药管理：医嘱/执行记录
- M5 膳食管理：食谱计划/点餐
- M6 健康档案：生命体征/评估
- M7 费用管理：计费项目/账单

### A2 OA 模块
- OA1 排班：班次模板/排班分配
- OA2 审批：申请单流转
- OA3 通知：站内通知发送
- OA4 培训：课程/学习记录

### B 模块
- B1 小程序服务闭环：服务请求工单
- B2 家属门户闭环：家属账号/探视预约
- B3 运营看板闭环：每日指标入库

## 数据迁移
```bash
cd backend
alembic upgrade head
```

## 新增 API 路由索引（本次）
- `/api/v1/m4-medication/*`
- `/api/v1/m5-meal/*`
- `/api/v1/m6-health/*`
- `/api/v1/m7-billing/*`
- `/api/v1/oa1-shift/*`
- `/api/v1/oa2-approval/*`
- `/api/v1/oa3-notification/*`
- `/api/v1/oa4-training/*`
- `/api/v1/b1-miniapp/*`
- `/api/v1/b2-family/*`
- `/api/v1/b3-dashboard/*`

## Web 页面（最小闭环）
登录后左侧菜单可进入对应页面，均提供“新增 + 列表”闭环。

## 自测步骤（逐模块）
1. 启动并登录，获取 TOKEN：
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"Admin@123456"}'
```
2. 每个模块先 POST 再 GET 验证：
   - M4: `POST /m4-medication/orders` -> `GET /m4-medication/orders`
   - M5: `POST /m5-meal/plans` -> `GET /m5-meal/plans`
   - M6: `POST /m6-health/vitals` -> `GET /m6-health/vitals`
   - M7: `POST /m7-billing/items` -> `GET /m7-billing/items`
   - OA1: `POST /oa1-shift/templates` -> `GET /oa1-shift/templates`
   - OA2: `POST /oa2-approval/requests` -> `GET /oa2-approval/requests`
   - OA3: `POST /oa3-notification/messages` -> `GET /oa3-notification/messages`
   - OA4: `POST /oa4-training/courses` -> `GET /oa4-training/courses`
   - B1: `POST /b1-miniapp/requests` -> `GET /b1-miniapp/requests`
   - B2: `POST /b2-family/accounts` -> `GET /b2-family/accounts`
   - B3: `POST /b3-dashboard/metrics` -> `GET /b3-dashboard/metrics`
3. Web 端逐项进入菜单，执行新增后确认表格出现新记录。
