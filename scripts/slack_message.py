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

    now = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y/%m/%d %H:%M")

    return f""":bar_chart: *BAA経営ダッシュボード*（{now}更新）

*■ 5期トラッキング（受注27社必達・7-12月）*
• 受注累計: {g("5期受注累計")} / {g("5期受注目標", "27")}社
• 在庫の期待受注: {g("在庫の期待受注")}社（目標27との差 {g("5期差分")}）
• 必要な新規アポ: 残り{g("必要な新規アポ")}件（月{g("月あたり必要アポ")}件ペース）
*■ 営業数字共有（当月）*
• 月内アポ合計: {g("月内アポ合計")}件（実施済 {g("月内アポ実施済")} / 残予定 {g("月内残アポ")}）
• 当月受注数: {g("当月受注数 (Jヨミ)")}件 （Jヨミ）
• 受注率: {g("受注率")} （(受注+Bヨミ)÷アポ実施数）
• Bヨミ: {g("Bヨミ")}件 / Cヨミ+: {g("Cヨミ+")}件 / Cヨミ−: {g("Cヨミ−")}件 / Dヨミ: {g("Dヨミ")}件
*■ 月次概要*
• 当月受注目標: {g("受注社数目標")}件 （5期27社の月別配分）
• 当月受注実績: {g("当月受注実績")}件
• 実質残必要受注: {g("実質残必要受注")}件 （=目標-実績-Bヨミ）
• 進捗率: {g("進捗率")}
• 受注ギャップ: {g("受注数ギャップ")}件 （目標 −(Jヨミ+Bヨミ)）
*■ 残必要アポ（当月分）*
• 標準 残必要アポ: {g("標準 残必要アポ")}件 （想定受注率29.5%・4期実測）
*■ 着地デッドライン*
• アポ取得締切: {g("アポ取得締切")}
• 締切まで残営業日: {g("締切まで残営業日")}日
*■ 注意事項*
:warning: 当月フェーズ未判定: {g("当月フェーズ未判定件数")}件 （要入力催促）

:link: 詳細: {DASHBOARD_URL}"""


def main() -> None:
    kpis = parse_kpis(fetch_sheet())
    if not kpis:
        sys.exit("KPI取得失敗: _LS シートが空")
    print(build_message(kpis))


if __name__ == "__main__":
    main()
