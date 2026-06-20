# actions-study

这是一个用于学习 GitHub Actions CI/CD 的 FastAPI 示例项目，使用 uv 管理 Python 环境和依赖。

## 本地开发

安装并同步依赖：

```powershell
uv sync
```

启动开发服务器：

```powershell
uv run fastapi dev app/main.py
```

打开接口文档：

```text
http://127.0.0.1:8000/docs
```

运行测试：

```powershell
uv run pytest
```

## CI

GitHub Actions 会在每次 push 到 `master` 或向 `master` 发起 pull request 时自动运行测试。

工作流文件：

```text
.github/workflows/ci.yml
```

学习笔记：

```text
CICD_LEARNING.md
```

## 本地模拟生产运行

```powershell
uv run fastapi run app/main.py --host 0.0.0.0 --port 8000
```
