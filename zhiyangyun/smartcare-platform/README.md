# 智慧养老平台（SmartCare Platform）

## 技术栈
- Backend: Python 3.11 / FastAPI / SQLAlchemy 2.0 / Alembic / PostgreSQL / Redis / JWT / bcrypt
- Web Admin: Vue3 + TypeScript + Vite + Element Plus + Pinia + Vue Router + Axios
- Mini Program: 微信小程序原生（后续按阶段实现）

## 当前进度
- A1-M1 资产与房间管理：已完成（后端+Web+迁移+初始化）
- 设计清单：`docs/M1_设计清单_资产与房间管理.md`

## 一键启动（Docker Compose）
```bash
cd infra
docker compose up -d --build
```

启动后：
- API: http://localhost:8000/docs
- Web: http://localhost:3000

默认账号：
- admin / Admin@123

## 本地开发

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python scripts/seed_m1.py
uvicorn app.main:app --reload --port 8000
```

### Web
```bash
cd web-admin
npm install
npm run dev
```

## M1 完成内容
- 多租户 tenant_id 全链路隔离（M1 覆盖表与查询）
- RBAC 最小可用（assets.read/write/delete）
- 资产模块：楼栋/楼层/房间/床位/概览/二维码占位
- 统一返回格式：`{success, message, data}`

## 下一步
- A1-M2 长者全周期管理（CRM基础、入院办理、床位分配、变更、退院）
