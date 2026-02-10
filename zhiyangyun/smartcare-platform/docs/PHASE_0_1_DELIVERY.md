# Phase 0 + Phase 1 交付说明

## 已完成

### Phase 0：工程基线
- Monorepo 目录建立
- 基础 README 与启动说明
- Infra Docker Compose（PostgreSQL / Redis / MinIO）

### Phase 1：可运行骨架
- Backend FastAPI 启动与健康检查
- 基础 API：`/api/v1/system/info`
- 示例业务 API：`/api/v1/elders`（内存版）
- Web Admin Next.js 启动首页
- WeChat Mini Program 原生骨架首页

## 目录结构

```
smartcare-platform/
├── backend/
├── web-admin/
├── mini-program/
├── infra/
└── docs/
```

## 进入 Phase 2 前的门禁检查

- [ ] 后端接入 PostgreSQL 真表（替换内存数据）
- [ ] Alembic 迁移初始化
- [ ] JWT 认证与 RBAC 最小集
- [ ] Web 登录页与权限路由守卫
- [ ] 关键接口单元测试

