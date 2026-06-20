# GitHub Actions CI/CD 学习笔记

这个项目用于边写边学 GitHub Actions CI/CD。当前后端使用 FastAPI，Python 环境和依赖由 uv 管理。

## 当前项目状态

- 应用框架：FastAPI
- 包管理和环境管理：uv
- 测试工具：pytest
- 仓库类型：GitHub private 仓库
- 当前分支：`master`
- 后续部署目标：阿里云 ECS，Ubuntu 22.04
- 计划使用域名：`action-study.ranjyaa.top`

## 学习路线

### 1. CI 基础

目标：每次提交代码后，自动运行测试。

已经完成：

- 创建 `.github/workflows/ci.yml`
- 在 push 到 `master` 或向 `master` 发起 pull request 时触发 CI
- 根据 `.python-version` 安装 Python
- 使用 `astral-sh/setup-uv` 安装 uv
- 使用 `uv sync --locked --dev` 还原依赖环境
- 使用 `uv run pytest` 运行测试

核心流程：

```text
push 代码 -> GitHub runner 启动 -> 安装依赖 -> 运行测试 -> 得到通过或失败结果
```

### 2. 增强 CI 质量

第一版 CI 稳定后，可以继续加入：

- 格式检查
- lint 检查
- 项目变复杂后加入类型检查
- 测试覆盖率报告
- 在 `README.md` 中加入 CI 状态徽章

可能使用的工具：

```text
ruff        格式化和 lint
pytest-cov  测试覆盖率
mypy        类型检查
```

### 3. 构建部署形态

目标：让应用具备稳定、可重复的部署方式。

计划学习：

- 编写生产用 Dockerfile
- 在服务器上使用 Docker Compose
- 约定应用暴露 `8000` 端口
- 使用 Caddy 或 Nginx 做反向代理
- 绑定域名 `action-study.ranjyaa.top`
- 配置 HTTPS

预期的生产运行命令：

```bash
uv run fastapi run app/main.py --host 0.0.0.0 --port 8000
```

### 4. CD 到 Ubuntu 服务器

目标：在部署分支 CI 通过后，自动部署到服务器。

计划流程：

```text
push 到 master
CI 测试通过
GitHub Actions 连接服务器
服务器拉取或接收新版本
服务重启
健康检查确认部署成功
```

预计需要的 GitHub Secrets：

```text
SERVER_HOST
SERVER_USER
SERVER_PORT
SERVER_SSH_KEY
```

如果后续使用容器镜像仓库，还可能需要：

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

### 5. 生产化实践

基础 CD 跑通后，继续学习：

- GitHub Environments
- 受保护的部署环境
- 生产部署前的人工审批
- 回滚策略
- 拆分 CI 和 CD 工作流
- 部署后的健康检查
- 密钥管理
- 服务器日志和可观测性

## CI 中用到的 uv 命令

严格按照 lockfile 安装依赖：

```bash
uv sync --locked --dev
```

在项目环境中运行测试：

```bash
uv run pytest
```

本地启动开发服务器：

```bash
uv run fastapi dev app/main.py
```

以接近生产的方式运行应用：

```bash
uv run fastapi run app/main.py --host 0.0.0.0 --port 8000
```

## 备注

- GitHub Actions 工作流文件使用 `.yml` 或 `.yaml` 都可以。
- `uv run` 会使用从当前项目目录发现的项目环境。
- 如果人在其他目录，可以使用 `uv --directory <project-path> run ...`。
- CI 中优先使用 `uv sync --locked --dev`，确保 runner 使用仓库提交的 `uv.lock`。
- 当前 workflow 固定使用 `astral-sh/setup-uv@v8.2.0`，没有使用 `@v8`，因为 major tag 可能无法稳定解析。
