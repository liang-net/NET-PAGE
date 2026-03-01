# NET-PAGE

轻量网络主页（静态页 + 管理后台），Docker 发布版。  
Lightweight personal homepage (static site + admin backend), Docker edition.

## Docker Image / 镜像地址

- `ghcr.io/vsss-net/net-page:latest`

## Default Port / 默认端口

- `3838` (host) -> `80` (container)

---

## 中文安装说明（详细）

### 1) 环境准备
- Linux 服务器（建议 Ubuntu 22.04/24.04）
- 已安装 Docker 与 Docker Compose 插件

安装（Ubuntu）：
```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker
```

### 2) 获取项目
```bash
git clone https://github.com/vsss-net/NET-PAGE.git
cd NET-PAGE
```

### 3) 修改后台账号密码（强烈建议）
编辑 `docker-compose.yml`：
- `ADMIN_USER`
- `ADMIN_PASS`

### 4) 启动
```bash
docker compose up -d --build
```

### 5) 访问
- 主页：`http://服务器IP:3838`
- 管理页：`http://服务器IP:3838/admin`

### 6) 更新
```bash
git pull
docker compose up -d --build
```

### 7) 停止与卸载
```bash
docker compose down
```

---

## English Installation Guide (Detailed)

### 1) Prerequisites
- Linux server (Ubuntu 22.04/24.04 recommended)
- Docker + Docker Compose plugin installed

Install on Ubuntu:
```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker
```

### 2) Clone repository
```bash
git clone https://github.com/vsss-net/NET-PAGE.git
cd NET-PAGE
```

### 3) Change admin credentials (strongly recommended)
Edit `docker-compose.yml`:
- `ADMIN_USER`
- `ADMIN_PASS`

### 4) Start services
```bash
docker compose up -d --build
```

### 5) Access
- Site: `http://SERVER_IP:3838`
- Admin: `http://SERVER_IP:3838/admin`

### 6) Upgrade
```bash
git pull
docker compose up -d --build
```

### 7) Stop
```bash
docker compose down
```
