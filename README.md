# BAA経営ダッシュボード（静的HTML版）

スプシ「BAA経営ダッシュボード_LS」シートのKPIを静的HTML 1枚にレンダリングし、GitHub Pagesで公開するシンプル構成。

## 構成

```
~/dev/baa-dashboard/
├── docs/<RANDOM_PATH>/index.html  ← GitHub Pages公開対象（生成物）
├── scripts/
│   └── generate.py                ← スプシ → HTML 生成
├── .url-path                      ← ランダムパス（.gitignore対象・秘密）
├── .gitignore
└── README.md
```

## セキュリティ

- リポは public（GitHub Pages無料プランの制約）
- URLパスは `secrets.token_urlsafe(6)` で生成したランダム文字列（例: `dAapsw5z`）
- 一般検索では発見困難。URLを知らない人はアクセス不可
- メタタグ `noindex, nofollow` で検索エンジンクロール拒否

## 公開URL

`https://rikutootsuka-prog.github.io/baa-dashboard/<RANDOM_PATH>/`

実際のRANDOM_PATHは `.url-path` ファイル内（push対象外）に保存。

## 使い方

### ローカル生成

```bash
python3 scripts/generate.py
```

→ `docs/<RANDOM_PATH>/index.html` を生成。

### 本番公開（push）

```bash
git add docs/
git commit -m "chore: update dashboard"
git push origin main
```

GitHub Pagesが自動デプロイ（数秒〜数十秒）。

### 更新頻度

- HTML自体は手動 or cronで再生成
- ブラウザ側で10分ごとに `<meta http-equiv="refresh">` で自動再読込

## データソース

- スプシID: `1fJlu1Ky2rNS3GepLGH2PUajE88kNzk9eqWGMf4m53aI`
- シート: `BAA経営ダッシュボード_LS`（指標／値／単位／グループの4列構造化）
- 取得: gws CLI（ローカル認証済み）

## 自動更新（オプション）

`crontab -e` に下記を追加すれば平日朝9時に自動再生成＆push：

```cron
0 9 * * 1-5 cd ~/dev/baa-dashboard && python3 scripts/generate.py && git add docs/ && git -c commit.gpgsign=false commit -m "chore: auto-update $(date +\%Y-\%m-\%d)" -q && git push origin main -q
```

## Slack DM配信との関係

別途 `~/.../BAA事業サポートスキル（共有）/scripts/baa_dashboard_daily.py` が平日朝にSlack DMでKPIサマリーを配信。
ダッシュボードURLはそのDM内にリンクとして埋め込み可能。
