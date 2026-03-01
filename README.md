# NET-PAGE

A lightweight bilingual (中文 / English) personal landing page template.

## Docker Image / 镜像地址

- `ghcr.io/vsss-net/net-page:latest`

---

## Features / 功能

- Language switch (ZH/EN) / 中英切换
- Shanghai timezone real-time clock with flip animation / 上海时区翻页时钟
- Visitor IP + location display / 访客 IP 与地区显示
- Weather display based on visitor location / 基于访客位置的天气展示
- Project cards section / 项目展示卡片
- Data-driven content from `data/site.json` / 内容由 `data/site.json` 驱动

---

## Quick Start (Docker) / Docker 快速启动

### 1) Requirements / 环境要求

- Docker 24+
- Docker Compose v2+

### 2) Run with image / 使用镜像启动（默认端口 3838）

```bash
docker run -d \
  --name net-page \
  -p 3838:80 \
  --restart unless-stopped \
  ghcr.io/vsss-net/net-page:latest
```

访问 / Access:
- <http://localhost:3838>

### 3) Run with Compose / 使用 Compose 启动（默认端口 3838）

```bash
git clone https://github.com/vsss-net/NET-PAGE.git
cd NET-PAGE
docker compose up -d
```

访问 / Access:
- <http://localhost:3838>

### 4) Stop / 停止

```bash
docker compose down
```

---

## Build locally / 本地构建镜像

```bash
docker build -t net-page:local .
docker run -d --name net-page-local -p 3838:80 net-page:local
```

---

## Manual Run (without Docker) / 非 Docker 运行

Use any static web server.

### Python example / Python 示例

```bash
cd NET-PAGE
python3 -m http.server 3838
```

Open / 访问:
- <http://localhost:3838>

---

## Content Configuration / 内容配置

Edit:

- `data/site.json`

Main fields:

- `siteTitle`: browser title / 浏览器标题
- `title`, `subtitle`: hero title/subtitle / 主标题与副标题
- `sectionTitle1..3`: section headings / 三个模块标题
- `about1..3`: section content / 三个模块内容
- `projectsTitle`: projects block title / 项目展示标题
- `projects`: project list array / 项目数组
  - `name`, `desc`, `status`, `link`
- `contact`: footer contact line / 底部联系

---

## Deploy to Server (Nginx) / 服务器部署（Nginx）

### 1) Copy files / 上传文件

Upload project files to server, e.g.:

- `/var/www/net-page`

### 2) Example Nginx config / Nginx 示例配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /var/www/net-page;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

### 3) Reload Nginx / 重载

```bash
sudo nginx -t && sudo systemctl reload nginx
```

---

## Notes / 说明

- This repository intentionally does **not** include private binding info, domains, API tokens, or certificate secrets.
- 本仓库不包含任何私有域名绑定、API Token、证书私钥等敏感信息。
