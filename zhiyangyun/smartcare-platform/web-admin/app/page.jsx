export default function Home() {
  return (
    <main style={{ padding: 24, fontFamily: 'sans-serif' }}>
      <h1>智慧养老管理端（Phase 1）</h1>
      <p>系统骨架已启动。下一阶段将接入认证、RBAC、主数据与任务闭环。</p>
      <ul>
        <li>后端健康检查：<code>GET /healthz</code></li>
        <li>系统信息：<code>GET /api/v1/system/info</code></li>
      </ul>
    </main>
  );
}
