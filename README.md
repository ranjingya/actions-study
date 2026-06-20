# actions-study

FastAPI project managed by uv.

## Development

Install and sync dependencies:

```powershell
uv sync
```

Run the development server:

```powershell
uv run fastapi dev app/main.py
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

Run tests:

```powershell
uv run pytest
```

## Production-style local run

```powershell
uv run fastapi run app/main.py --host 0.0.0.0 --port 8000
```
