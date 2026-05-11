# BAA 経営ダッシュボード

BAA事業の月次受注目標に対する着地予測を可視化するダッシュボード。

## アーキテクチャ

- **Frontend**: Next.js 16 (App Router) + React 19 + Tailwind CSS 4
- **Backend**: Next.js API Routes
- **Data Source**: Google Sheets (BAA営業データベース「BAA経営ダッシュボード」シート)
- **Hosting**: Vercel
- **Notification**: Slack DM (別途 `scripts/baa_dashboard_daily.py` で配信)

## データフロー

```
Google Sheets (関数集計)
  └── /api/kpi (Service Account)
        └── /  (React + SWR・1分自動更新)
```

## 開発

```bash
pnpm install
pnpm dev   # http://localhost:3000
```

ローカル開発時は `gws` CLI 経由で動作（環境変数不要）。

## 本番デプロイ（Vercel）

### 1. Service Account を作成

1. https://console.cloud.google.com/apis/credentials
2. **CREATE CREDENTIALS** → **Service account**
3. **Keys** → **ADD KEY** → JSON で `credentials.json` をダウンロード

### 2. スプシを Service Account にシェア

対象スプシ:
- ID: `1fJlu1Ky2rNS3GepLGH2PUajE88kNzk9eqWGMf4m53aI`
- Service Accountのメアド（例: `xxx@xxx.iam.gserviceaccount.com`）を **閲覧者** として共有

### 3. Vercel環境変数に登録

```bash
base64 -i credentials.json | pbcopy
vercel env add GOOGLE_SHEETS_CREDENTIALS_BASE64 production
```

### 4. デプロイ

```bash
vercel --prod
```

## 環境変数

| 変数名 | 必須 | 説明 |
|---|---|---|
| `GOOGLE_SHEETS_CREDENTIALS_BASE64` | 本番のみ | Service Account credentialsをbase64化したもの |
