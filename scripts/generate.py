#!/usr/bin/env python3
"""
BAA経営ダッシュボード HTML生成スクリプト

スプシ「BAA経営ダッシュボード_LS」シートからKPI値を取得し、
docs/<RANDOM_PATH>/index.html を生成する。

実行:
  python3 scripts/generate.py

依存: gws CLI (Google Workspace CLI)
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
GWS_CLI = "/Users/ootsukarikuto/.nvm/versions/node/v22.17.0/bin/gws"
SHEET_ID = "1fJlu1Ky2rNS3GepLGH2PUajE88kNzk9eqWGMf4m53aI"
SHEET_NAME = "BAA経営ダッシュボード_LS"
RANGE = f"{SHEET_NAME}!A1:D30"


def read_url_path() -> str:
    p = ROOT / ".url-path"
    if not p.exists():
        sys.exit(".url-path が見つかりません。secrets.token_urlsafe(6) で生成してください。")
    return p.read_text().strip()


def fetch_sheet() -> list[list[str]]:
    params = json.dumps({"spreadsheetId": SHEET_ID, "range": RANGE})
    result = subprocess.run(
        [GWS_CLI, "sheets", "spreadsheets", "values", "get", "--params", params],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    return data.get("values", [])


def parse_kpis(rows: list[list[str]]) -> dict[str, dict]:
    """A列=指標名、B列=値、C列=単位、D列=グループ をdictへ"""
    kpis = {}
    for row in rows[1:]:  # skip header
        if len(row) < 2:
            continue
        name = row[0]
        value = row[1] if len(row) > 1 else ""
        unit = row[2] if len(row) > 2 else ""
        group = row[3] if len(row) > 3 else ""
        kpis[name] = {"value": value, "unit": unit, "group": group}
    return kpis


def g_val(kpis: dict, key: str, default: str = "-") -> str:
    k = kpis.get(key)
    return str(k["value"]) if k else default


def render_html(kpis: dict[str, dict]) -> str:
    now = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M")

    def card(key: str, label: str, *, big: bool = False, color: str = "default", note: str = "") -> str:
        k = kpis.get(key)
        if not k:
            return f'<div class="card">{label}: -</div>'
        size_class = "card-big" if big else "card"
        color_class = f" card-{color}" if color != "default" else ""
        note_html = f'<div class="card-note">{note}</div>' if note else ""
        return (
            f'<div class="{size_class}{color_class}">'
            f'<div class="card-label">{label}</div>'
            f'<div class="card-value">{k["value"]}</div>'
            f'<div class="card-unit">{k["unit"]}</div>'
            f"{note_html}"
            f"</div>"
        )

    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<title>BAA経営ダッシュボード</title>
<meta http-equiv="refresh" content="600">
<style>
:root {{
  --bg: #f8fafc;
  --panel: #ffffff;
  --border: #e2e8f0;
  --text: #0f172a;
  --muted: #64748b;
  --accent: #1d4ed8;
  --red: #dc2626;
  --green: #16a34a;
  --orange: #ea580c;
}}
* {{ box-sizing: border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Yu Gothic", sans-serif;
  background: var(--bg);
  color: var(--text);
  margin: 0;
  padding: 24px 16px 48px;
  line-height: 1.5;
}}
.container {{ max-width: 1100px; margin: 0 auto; }}
header {{
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 8px;
}}
h1 {{ margin: 0; font-size: 24px; letter-spacing: 0.02em; }}
.meta {{ font-size: 12px; color: var(--muted); }}
.section-title {{
  font-size: 14px;
  font-weight: 600;
  color: var(--muted);
  margin: 28px 0 12px;
  letter-spacing: 0.08em;
}}
.grid {{ display: grid; gap: 12px; }}
.grid-7 {{ grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); }}
.grid-3 {{ grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }}

.card, .card-big {{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px 18px;
  transition: transform 0.1s;
}}
.card:hover, .card-big:hover {{ transform: translateY(-1px); }}
.card-label {{
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 6px;
  letter-spacing: 0.02em;
}}
.card-value {{
  font-size: 32px;
  font-weight: 700;
  font-feature-settings: "tnum";
  letter-spacing: -0.02em;
  color: var(--text);
}}
.card-big .card-value {{ font-size: 44px; }}
.card-unit {{
  font-size: 11px;
  color: var(--muted);
  margin-top: 2px;
}}
.card-note {{
  font-size: 10px;
  color: var(--muted);
  margin-top: 6px;
  line-height: 1.35;
}}
.card-red .card-value {{ color: var(--red); }}
.card-green .card-value {{ color: var(--green); }}
.card-orange .card-value {{ color: var(--orange); }}
.card-accent .card-value {{ color: var(--accent); }}

footer {{
  margin-top: 40px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
  font-size: 11px;
  color: var(--muted);
  text-align: center;
}}
footer a {{ color: var(--accent); text-decoration: none; }}

@media (max-width: 480px) {{
  body {{ padding: 16px 12px 32px; }}
  h1 {{ font-size: 20px; }}
  .card-value {{ font-size: 26px; }}
  .card-big .card-value {{ font-size: 34px; }}
}}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>📊 BAA経営ダッシュボード</h1>
    <div class="meta">最終更新: {now}（10分ごと自動再読込）</div>
  </header>

  <div class="section-title">5期トラッキング（受注27社必達・7-12月）</div>
  <div class="grid grid-3">
    {card("5期受注累計", "🏁 5期受注累計", big=True, color="green", note=f"目標 {g_val(kpis, "5期受注目標", "27")}社（7-12月）")}
    {card("在庫の期待受注", "📦 在庫の期待受注", big=True, color="accent", note=f"ヨミ在庫×確度の期待値。目標27との差 {g_val(kpis, "5期差分")}社")}
    {card("必要な新規アポ", "🔥 必要な新規アポ", big=True, color="red", note=f"残り件数。月{g_val(kpis, "月あたり必要アポ")}件ペースで積む")}
  </div>

  <div class="section-title">月次概要（当月）</div>
  <div class="grid grid-3">
    {card("受注社数目標", "🎯 当月受注目標", big=True, color="accent", note="5期27社の月別配分")}
    {card("受注数ギャップ", "⚡ 当月受注ギャップ", big=True, color="red", note="当月目標 − (Jヨミ + Bヨミ)")}
    {card("標準 残必要アポ", "📌 当月残必要アポ", big=True, color="orange", note="当月分のみ。5期全体は上段「必要な新規アポ」を見る")}
  </div>

  <div class="section-title">営業数字共有（当月）</div>
  <div class="grid grid-7">
    {card("月内アポ合計", "📅 月内アポ合計", note="実施済 + 残予定")}
    {card("月内アポ実施済", "✔️ 実施済", note="本日までに実施したアポ件数")}
    {card("月内残アポ", "🗓 月内残アポ", color="accent", note="今日以降〜月末に予定済のアポ件数")}
    {card("当月受注数 (Jヨミ)", "✅ 受注", color="green")}
    {card("受注率", "📈 受注率", color="green", note="(受注+Bヨミ)÷アポ実施数")}
    {card("Bヨミ", "Bヨミ")}
    {card("Cヨミ+", "Cヨミ+")}
    {card("Cヨミ−", "Cヨミ−")}
    {card("Dヨミ", "Dヨミ")}
  </div>

  <footer>
    Powered by Python + GitHub Pages
  </footer>
</div>
</body>
</html>
"""


def main() -> None:
    url_path = read_url_path()
    rows = fetch_sheet()
    kpis = parse_kpis(rows)
    html = render_html(kpis)

    out_dir = ROOT / "docs" / url_path
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "index.html"
    out_file.write_text(html, encoding="utf-8")

    print(f"✅ Generated: {out_file}")
    print(f"   URL path: /{url_path}/")
    print(f"   KPIs:     {len(kpis)} entries")


if __name__ == "__main__":
    main()
