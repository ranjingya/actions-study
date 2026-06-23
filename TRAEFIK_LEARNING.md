# Traefik 网关学习笔记

本文记录当前项目使用 Traefik 作为统一反向代理和 HTTPS 网关的学习过程。

## 目标

把服务器上的公网入口统一交给 Traefik：

```text
用户访问域名
-> DNS 解析到服务器公网 IP
-> Traefik 监听 80/443
-> Traefik 根据域名匹配业务容器
-> 转发到业务容器内部端口
```

业务容器以后不直接暴露公网端口，只加入 Traefik 的公共 Docker 网络，并通过 labels 声明路由规则。

## 当前服务器端口关系

当前服务器上已有：

```text
80/443  -> Traefik
9998    -> Nginx 容器
9999    -> CrashCore
```

Nginx 容器使用 host 网络，但配置中只监听 `9998`：

```nginx
listen 9998;
```

所以它不会和 Traefik 的 `80/443` 冲突。

端口是否冲突可以用下面命令确认：

```bash
sudo ss -lntp | grep -E ':80|:443|:9998|:9999'
```

同一台服务器同一个 IP 的同一个端口只能被一个服务监听。如果 Nginx 监听了 `80/443`，Traefik 再暴露 `80/443` 就会冲突。

## 域名访问流程

Traefik 不是监听 DNS 变化，而是监听服务器端口。

流程如下：

```text
1. 用户访问 https://action-study.ranjyaa.top
2. 浏览器查询 DNS
3. DNS 返回服务器公网 IP
4. 浏览器连接 服务器 IP:443
5. Traefik 接收到 HTTPS 请求
6. Traefik 读取请求域名
7. Traefik 用 Host(`action-study.ranjyaa.top`) 匹配 router
8. Traefik 转发到业务容器内部端口
```

业务容器通过 labels 告诉 Traefik：

```yaml
traefik.http.routers.actions-study.rule: "Host(`action-study.ranjyaa.top`)"
```

## ACME 和 Challenge

Let's Encrypt 是免费证书机构。

ACME 是自动申请和续期 HTTPS 证书的协议。Traefik 可以作为 ACME 客户端，自动向 Let's Encrypt 申请证书。

申请证书时，Let's Encrypt 会要求证明域名归属，这一步叫 Challenge。

常见 Challenge 有两种：

```text
HTTP Challenge
DNS Challenge
```

### HTTP Challenge

HTTP Challenge 使用固定路径验证：

```text
http://域名/.well-known/acme-challenge/<token>
```

其中：

```text
/.well-known/acme-challenge/
```

是 ACME HTTP-01 Challenge 规定的固定路径。

Traefik 会自动处理这个路径，不需要业务应用实现接口。

HTTP Challenge 要求：

```text
域名 A 记录指向服务器
服务器 80 端口公网可访问
Traefik 监听 80
```

HTTP Challenge 配置简单，但不能申请泛域名证书。

### DNS Challenge

DNS Challenge 通过 DNS TXT 记录证明域名归属。

Let's Encrypt 会要求创建类似：

```text
_acme-challenge.ranjyaa.top TXT "验证内容"
```

Traefik 通过 DNS 服务商 API 自动创建和删除 TXT 记录。

DNS Challenge 不依赖服务器 80 端口，并且支持泛域名证书。

当前计划使用：

```text
DNS 服务商：alidns
ACME 邮箱：ranjyaa@qq.com
```

## TXT 记录是什么

DNS 记录类型包括：

```text
A       域名指向 IPv4
AAAA    域名指向 IPv6
CNAME   域名指向另一个域名
MX      邮件服务器
TXT     文本记录
```

DNS Challenge 使用 TXT 记录存放验证内容。

如果 Let's Encrypt 能查询到正确 TXT 内容，就证明你能控制这个域名的 DNS，因此可以签发证书。

## 泛域名证书

普通证书只覆盖一个具体域名：

```text
action-study.ranjyaa.top
```

泛域名证书覆盖一批一级子域名：

```text
*.ranjyaa.top
```

它可以覆盖：

```text
action-study.ranjyaa.top
api.ranjyaa.top
blog.ranjyaa.top
```

通常不覆盖更深层级：

```text
a.b.ranjyaa.top
```

DNS Challenge 不等于一定申请泛域名证书。DNS Challenge 只是验证方式，是否申请泛域名取决于 Traefik 配置里声明的证书域名。

## 显式申请泛域名证书

推荐把泛域名证书声明放在 Traefik 网关自己的动态配置里，而不是挂在某个业务容器 labels 上。

目录结构：

```text
~/.traefik
├── docker-compose.yaml
├── .env
├── dynamic
│   └── tls.yaml
└── letsencrypt
    └── acme.json
```

创建目录：

```bash
mkdir -p ~/.traefik/dynamic
mkdir -p ~/.traefik/letsencrypt
touch ~/.traefik/letsencrypt/acme.json
chmod 600 ~/.traefik/letsencrypt/acme.json
```

`acme.json` 会保存证书、私钥和 ACME 账号信息，不能提交到 Git。

## Traefik 网关 Compose

`~/.traefik/docker-compose.yaml`：

```yaml
services:
  traefik:
    image: traefik:v3
    container_name: traefik
    restart: unless-stopped
    command:
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--providers.docker.network=traefik-network"

      - "--providers.file.directory=/etc/traefik/dynamic"
      - "--providers.file.watch=true"

      - "--entrypoints.web.address=:80"
      - "--entrypoints.web.http.redirections.entrypoint.to=websecure"
      - "--entrypoints.web.http.redirections.entrypoint.scheme=https"
      - "--entrypoints.websecure.address=:443"

      - "--certificatesresolvers.myresolver.acme.email=ranjyaa@qq.com"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.myresolver.acme.dnschallenge=true"
      - "--certificatesresolvers.myresolver.acme.dnschallenge.provider=alidns"

    environment:
      ALICLOUD_ACCESS_KEY: "${ALICLOUD_ACCESS_KEY}"
      ALICLOUD_SECRET_KEY: "${ALICLOUD_SECRET_KEY}"

    ports:
      - "80:80"
      - "443:443"

    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./dynamic:/etc/traefik/dynamic:ro"
      - "./letsencrypt:/letsencrypt"

    networks:
      - traefik-network

networks:
  traefik-network:
    external: true
```

`.env`：

```env
ALICLOUD_ACCESS_KEY=你的阿里云 AccessKeyId
ALICLOUD_SECRET_KEY=你的阿里云 AccessKeySecret
```

创建公共网络：

```bash
docker network create traefik-network
```

启动 Traefik：

```bash
cd ~/.traefik
docker compose up -d
```

## 动态 TLS 配置

`~/.traefik/dynamic/tls.yaml`：

```yaml
tls:
  stores:
    default:
      defaultGeneratedCert:
        resolver: myresolver
        domain:
          main: ranjyaa.top
          sans:
            - "*.ranjyaa.top"
```

这表示让 Traefik 使用 `myresolver` 申请并维护：

```text
ranjyaa.top
*.ranjyaa.top
```

证书会保存到：

```text
~/.traefik/letsencrypt/acme.json
```

以后其他 `*.ranjyaa.top` 的业务容器可以复用这张泛域名证书。

## `:ro` 的含义

Docker volume 后面的 `:ro` 表示 read-only，只读挂载。

例如：

```yaml
- "./dynamic:/etc/traefik/dynamic:ro"
```

表示容器只能读取动态配置，不能修改它。

证书目录不能加 `:ro`：

```yaml
- "./letsencrypt:/letsencrypt"
```

因为 Traefik 需要写入和续期证书。

## 业务容器接入 Traefik

业务容器不再直接暴露公网端口，不写：

```yaml
ports:
  - "8000:8000"
```

而是写：

```yaml
expose:
  - "8000"
```

并加入 `traefik-network`。

当前项目可以这样接入：

```yaml
services:
  actions-study:
    image: ghcr.io/ranjingya/actions-study:latest
    container_name: actions-study
    restart: unless-stopped
    expose:
      - "8000"
    labels:
      traefik.enable: "true"
      traefik.docker.network: traefik-network
      traefik.http.routers.actions-study.rule: "Host(`action-study.ranjyaa.top`)"
      traefik.http.routers.actions-study.entrypoints: websecure
      traefik.http.routers.actions-study.tls: "true"
      traefik.http.routers.actions-study.tls.certresolver: myresolver
      traefik.http.services.actions-study.loadbalancer.server.port: 8000
    networks:
      - traefik-network

networks:
  traefik-network:
    external: true
```

这里的服务名：

```yaml
services:
  actions-study:
```

要和 CD 中执行的服务名一致：

```bash
docker compose pull actions-study
docker compose up -d --remove-orphans actions-study
```

## 一个容器加入多个网络

同一个容器可以加入多个 Docker network。

如果服务器用 ShellCrash，并且需要把某些容器加入代理网络，例如：

```text
test 网络：172.16.0.0/16
traefik-network：Traefik 反向代理网络
```

业务容器可以同时加入：

```yaml
networks:
  - test
  - traefik-network
```

同时要指定 Traefik 使用哪个网络访问业务容器：

```yaml
traefik.docker.network: traefik-network
```

否则 Traefik 可能选错网络。

示例：

```yaml
services:
  actions-study:
    image: ghcr.io/ranjingya/actions-study:latest
    expose:
      - "8000"
    labels:
      traefik.enable: "true"
      traefik.docker.network: traefik-network
      traefik.http.routers.actions-study.rule: "Host(`action-study.ranjyaa.top`)"
      traefik.http.routers.actions-study.entrypoints: websecure
      traefik.http.routers.actions-study.tls: "true"
      traefik.http.routers.actions-study.tls.certresolver: myresolver
      traefik.http.services.actions-study.loadbalancer.server.port: 8000
    networks:
      - test
      - traefik-network

networks:
  test:
    external: true
  traefik-network:
    external: true
```

## 总结

推荐架构：

```text
Traefik 单独部署，长期占用 80/443
业务容器加入 traefik-network
业务容器通过 labels 声明域名和内部端口
Traefik 使用 DNS Challenge 向 Let's Encrypt 申请泛域名证书
证书保存在 ~/.traefik/letsencrypt/acme.json
后续子域名服务复用泛域名证书
```

当前项目接入后，访问链路是：

```text
https://action-study.ranjyaa.top
-> DNS 指向服务器
-> Traefik 443
-> Host(`action-study.ranjyaa.top`)
-> actions-study:8000
-> FastAPI
```
