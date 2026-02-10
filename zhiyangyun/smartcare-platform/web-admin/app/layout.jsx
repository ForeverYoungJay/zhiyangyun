export const metadata = {
  title: 'SmartCare Web Admin',
  description: '智慧养老管理端',
};

export default function RootLayout({ children }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
