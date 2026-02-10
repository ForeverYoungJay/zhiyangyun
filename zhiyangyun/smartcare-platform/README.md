# 智慧养老平台（SmartCare Platform）

单仓工程（Monorepo）：
- `backend`：FastAPI + PostgreSQL + Redis
- `web-admin`：Next.js 管理端
- `mini-program`：微信小程序（原生）骨架
- `infra`：Docker Compose 与基础运维配置
- `docs`：阶段交付与设计文档

## 阶段推进（严格门禁）

- Phase 0：工程基线与规范（完成）
- Phase 1：可运行系统骨架（完成）
- Phase 2：认证/RBAC/主数据
- Phase 3：护理任务闭环 + 扫码
- Phase 4：财务闭环 + 审计
- Phase 5：家属小程序核心链路
- Phase 6：联调、压测、上线

## 本地快速启动

### 1) 启动依赖
```bash
cd infra
docker compose up -d
```

### 2) 启动后端
```bash
cd ../backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3) 启动 Web 管理端
```bash
cd ../web-admin
npm install
npm run dev
```

## 接口健康检查
- `GET http://localhost:8000/healthz`
- `GET http://localhost:8000/api/v1/system/info`

