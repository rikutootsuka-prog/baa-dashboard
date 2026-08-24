#!/usr/bin/env python3
"""BAA経営ダッシュボード Slack配信メッセージ生成

ダッシュボード本体(generate.py)と完全に同じデータ源
（スプシ「BAA経営ダッシュボード_LS」シート）から取得し、
Slack投稿用の本文を stdout に出力する。

★なぜ generate.py を再利用するか:
  旧 baa-skill/scripts/baa_dashboard_daily.py は別シート(gid=1573501633)を
  読んでおり「月内アポ実施=0」など誤値を出すバグがあった。
  ダッシュボードに表示される正しい数字は _LS シート経由なので、
  配信も必ず同じ fetch_sheet()/parse_kpis() を使い、表示と配信を一致させる。

実行: python3 scripts/slack_message.py
依存: gws CLI（generate.py と共通）
"""

import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate import fetch_sheet, parse_kpis  # noqa: E402

DASHBOARD_URL = "https://rikutootsuka-prog.github.io/baa-dashboard/dAapsw5z/"


def build_message(kpis: dict) -> str:
    def g(key: str, default: str = "-") -> str:
        k = kpis.get(key)
        return str(k["value"]) if k else default

    def pct(num: str, den: str) -> str:
        try:
            n, d = float(num), float(den)
            return f"（達成率 {n / d:.1%}）" if d else ""
        except (TypeError, ValueError):
            return ""

    now = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y/%m/%d %H:%M")
    m_target, m_actual = g("受注社数目標"), g("当月受注数 (Jヨミ)")
    q_target, q_actual = g("当Q受注目標"), g("当Q受注数")

    return f""":bar_chart: *BAA経営ダッシュボード*（{now}更新）

*■ 当月（{g("当月締め窓")}）*
• 受注目標: {m_target}社
• 受注数: {m_actual}社{pct(m_actual, m_target)}

*■ 当四半期（{g("当Qラベル")}）*
• 受注目標: {q_target}社
• 受注数: {q_actual}社{pct(q_actual, q_target)}

:link: 詳細（残アポ・ヨミ内訳など）: {DASHBOARD_URL}
_受注社数のカウントは2026年9月分から20日締め（前月21日〜当月20日）。8月分までは月内まるまる。_"""


def main() -> None:
    kpis = parse_kpis(fetch_sheet())
    if not kpis:
        sys.exit("KPI取得失敗: _LS シートが空")
    print(build_message(kpis))


if __name__ == "__main__":
    main()
