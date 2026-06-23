from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.core.config import get_settings

router = APIRouter(tags=["home"])


@router.get("/", response_class=HTMLResponse)
def read_home() -> str:
    settings = get_settings()
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{settings.app_name}</title>
    <style>
      :root {{
        color-scheme: dark;
        --bg: #0b0f14;
        --panel: #111820;
        --line: #263241;
        --text: #e7edf3;
        --muted: #91a0af;
        --accent: #8fb7d6;
      }}

      * {{
        box-sizing: border-box;
      }}

      body {{
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        background:
          linear-gradient(180deg, rgba(255, 255, 255, 0.03), transparent 28%),
          var(--bg);
        color: var(--text);
        font-family:
          Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
          "Segoe UI", sans-serif;
      }}

      main {{
        width: min(680px, calc(100vw - 40px));
        border: 1px solid var(--line);
        background: rgba(17, 24, 32, 0.86);
        padding: 40px;
      }}

      .mark {{
        width: 36px;
        height: 2px;
        margin-bottom: 28px;
        background: var(--accent);
      }}

      h1 {{
        margin: 0;
        font-size: clamp(32px, 5vw, 56px);
        font-weight: 650;
        line-height: 1;
        letter-spacing: 0;
      }}

      p {{
        max-width: 560px;
        margin: 18px 0 0;
        color: var(--muted);
        font-size: 16px;
        line-height: 1.8;
      }}

      dl {{
        display: grid;
        grid-template-columns: max-content 1fr;
        gap: 12px 22px;
        margin: 34px 0 0;
        padding-top: 24px;
        border-top: 1px solid var(--line);
      }}

      dt {{
        color: var(--muted);
      }}

      dd {{
        margin: 0;
        color: var(--text);
      }}

      a {{
        color: var(--accent);
        text-decoration: none;
      }}

      a:hover {{
        text-decoration: underline;
      }}

      @media (max-width: 520px) {{
        main {{
          padding: 28px;
        }}

        dl {{
          grid-template-columns: 1fr;
          gap: 6px;
        }}
      }}
    </style>
  </head>
  <body>
    <main>
      <div class="mark" aria-hidden="true"></div>
      <h1>{settings.app_name}</h1>
      <p>
        A compact FastAPI service deployed through a measured CI/CD path:
        tests, container image, registry, and controlled server rollout.
      </p>
      <dl>
        <dt>Status</dt>
        <dd><a href="/health">/health</a></dd>
        <dt>Version</dt>
        <dd>{settings.app_version}</dd>
        <dt>Environment</dt>
        <dd>{settings.environment}</dd>
      </dl>
    </main>
  </body>
</html>"""
