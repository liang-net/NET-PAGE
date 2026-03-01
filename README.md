# NET-PAGE

中文/英文切换的个人介绍页模板，带：
- 上海时区实时时钟（翻页动画）
- 访客 IP + 地理位置显示
- 天气实时展示（按访问地）
- 项目展示卡片

## 本地运行
```bash
docker compose up -d --build
```
访问：`http://localhost:8080`

## 目录
- `index.html` 主页
- `app.js` 交互逻辑
- `data/site.json` 内容数据
