# 智慧养老平台（阶段 A1-M1：资产与房间管理）

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
- M1 资产与房间管理：楼栋 / 楼层 / 房间 / 床位 / 床位状态 / 二维码值

## 数据迁移
```bash
cd backend
alembic upgrade head
```

## 关键 API 示例
### 登录
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"Admin@123456"}'
```

### 新增楼栋
```bash
curl -X POST http://localhost:8000/api/v1/assets/buildings \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"name":"B栋","code":"B"}'
```

### 更新床位状态
```bash
curl -X PATCH http://localhost:8000/api/v1/assets/beds/{bed_id}/status \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"status":"occupied"}'
```
