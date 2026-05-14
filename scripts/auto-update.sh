#!/bin/bash
# BAA経営ダッシュボード 自動更新スクリプト
# crontab に登録して定期実行する。
#
# 登録例（crontab -e）:
#   # 平日朝9:00に自動更新
#   0 9 * * 1-5 /Users/ootsukarikuto/dev/baa-dashboard/scripts/auto-update.sh >> /tmp/baa-dashboard.log 2>&1
#
# 動作:
#   1. リモートから rebase pull（手動編集との競合回避）
#   2. scripts/generate.py で HTML 再生成
#   3. 変更があれば commit & push
#   4. 変更なしならスキップ

set -e

cd "$(dirname "$0")/.."

# PATH 補完（cron 実行時は環境変数が最小限）
# /opt/homebrew/bin は gh CLI (credential helper) のため必須
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/Users/ootsukarikuto/.nvm/versions/node/v22.17.0/bin:$PATH"

echo "===== $(date '+%Y-%m-%d %H:%M:%S') ====="

# 1. リモートと同期
git pull --rebase origin main 2>/dev/null || true

# 2. HTML 生成
python3 scripts/generate.py

# 3. 差分があれば commit & push
if [ -n "$(git status --porcelain docs/)" ]; then
  git add docs/
  git -c commit.gpgsign=false commit -m "chore: auto-update $(date +%Y-%m-%d)" -q
  git push origin main -q
  echo "✅ Updated and pushed"
else
  echo "✓ No changes"
fi
