'use client';
import useSWR from 'swr';
import type { KPI } from '@/lib/kpi';

const fetcher = (url: string) =>
  fetch(url).then((r) => {
    if (!r.ok) throw new Error('Failed to fetch');
    return r.json() as Promise<KPI>;
  });

const SHEET_URL =
  'https://docs.google.com/spreadsheets/d/1fJlu1Ky2rNS3GepLGH2PUajE88kNzk9eqWGMf4m53aI/edit?gid=1573501633';

export default function Dashboard() {
  const { data, error, isLoading } = useSWR<KPI>('/api/kpi', fetcher, {
    refreshInterval: 60000,
    revalidateOnFocus: true,
  });

  if (isLoading) {
    return (
      <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <div className="text-slate-400 text-lg animate-pulse">Loading...</div>
      </main>
    );
  }
  if (error) {
    return (
      <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <div className="text-red-400">
          Error: {error instanceof Error ? error.message : 'Unknown'}
        </div>
      </main>
    );
  }
  if (!data) return null;

  const progressPct = Math.min(100, data.forecast.progress * 100);

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* ヘッダー */}
        <header className="mb-10">
          <div className="flex flex-wrap items-baseline justify-between gap-4 mb-2">
            <h1 className="text-3xl md:text-4xl font-bold tracking-tight">
              <span className="bg-gradient-to-r from-sky-400 to-emerald-400 bg-clip-text text-transparent">
                📊 BAA経営ダッシュボード
              </span>
            </h1>
            <div className="text-sm text-slate-400">
              対象月 <span className="text-slate-200 font-mono">{data.targetMonth}</span>
              <span className="mx-2 text-slate-600">|</span>
              最終更新 <span className="text-slate-300 font-mono">{data.lastUpdated}</span>
            </div>
          </div>
          <p className="text-slate-500 text-sm">関数連動・1分ごと自動更新</p>
        </header>

        {/* セクション: 着地予測 (Hero) */}
        <section className="mb-10">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <HeroCard
              label="🎯 目標"
              value={data.forecast.target}
              suffix="件"
              variant="default"
            />
            <HeroCard
              label="🔥 実質残必要受注"
              value={data.forecast.remaining}
              suffix="件"
              variant="danger"
              sub={`実績 ${data.forecast.achieved}件 + Bヨミ ${data.forecast.bYomi}件 を差し引き`}
            />
            <HeroCard
              label="📌 残必要アポ"
              value={data.required.standardApo}
              suffix="件"
              variant="primary"
              sub={`想定受注率 ${Math.round(data.required.rate * 100)}%`}
            />
          </div>

          {/* プログレスバー */}
          <div className="mt-6 bg-slate-900/60 rounded-xl p-5 border border-slate-800">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-slate-400">月次進捗（実績+Bヨミ）</span>
              <span className="font-mono">
                <span className="font-bold text-emerald-400">
                  {data.forecast.achieved + data.forecast.bYomi}
                </span>
                <span className="text-slate-500"> / {data.forecast.target}件</span>
                <span className="ml-3 text-slate-300">
                  {(data.forecast.progress * 100).toFixed(1)}%
                </span>
              </span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-3 overflow-hidden">
              <div
                className="bg-gradient-to-r from-emerald-500 to-sky-400 h-3 rounded-full transition-all duration-700"
                style={{ width: `${progressPct}%` }}
              />
            </div>
          </div>
        </section>

        {/* セクション: 営業数字共有 */}
        <section className="mb-10">
          <SectionTitle>📈 営業数字共有</SectionTitle>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
            <MiniCard label="月内アポ実施" value={data.sales.apoTotal} />
            <MiniCard
              label="当月受注"
              value={data.sales.juchu}
              highlight={data.sales.juchu > 0 ? 'success' : undefined}
            />
            <MiniCard label="Bヨミ" value={data.sales.bYomi} />
            <MiniCard label="Cヨミ+" value={data.sales.cPlus} />
            <MiniCard label="Cヨミ−" value={data.sales.cMinus} />
            <MiniCard label="Dヨミ" value={data.sales.dYomi} />
            <MiniCard label="繰越" value={data.sales.kurikoshi} />
          </div>
        </section>

        {/* セクション: デッドライン */}
        <section className="mb-10">
          <SectionTitle>⏰ 着地デッドライン</SectionTitle>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <InfoCard label="月末日" value={data.deadline.monthEnd} tone="muted" />
            <InfoCard
              label="アポ取得締切 (5営業日前)"
              value={data.deadline.apoDeadline}
              tone="warning"
            />
            <InfoCard
              label="締切まで残営業日"
              value={`${data.deadline.daysLeft} 営業日`}
              tone="primary"
            />
          </div>
        </section>

        {/* セクション: 注意事項 */}
        {data.alerts.phaseUnset > 0 && (
          <section className="mb-10">
            <div className="bg-amber-950/40 border border-amber-700/50 rounded-xl p-5">
              <div className="flex items-start gap-3">
                <div className="text-2xl">⚠️</div>
                <div>
                  <div className="font-bold text-amber-300 mb-1">
                    フェーズ未判定 {data.alerts.phaseUnset}件
                  </div>
                  <div className="text-sm text-amber-100/70">
                    当月アポ実施分のうち、フェーズ（Bヨミ/Cヨミ+等）が未入力の案件があります。担当者に入力依頼してください。
                  </div>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* フッター */}
        <footer className="text-center text-sm text-slate-500 pt-8 border-t border-slate-800">
          <a
            href={SHEET_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sky-400 hover:text-sky-300 underline"
          >
            📋 元データのスプレッドシートを開く
          </a>
          <span className="mx-3 text-slate-700">|</span>
          <span>BAA事業 / Build AI Academy</span>
        </footer>
      </div>
    </main>
  );
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-lg font-bold mb-3 text-slate-300 flex items-center gap-2">
      {children}
    </h2>
  );
}

function HeroCard({
  label,
  value,
  suffix,
  variant,
  sub,
}: {
  label: string;
  value: number;
  suffix: string;
  variant: 'default' | 'danger' | 'primary';
  sub?: string;
}) {
  const variantClass = {
    default: 'from-slate-800/60 to-slate-900/60 border-slate-700/50 text-white',
    danger: 'from-red-950/50 to-slate-900/60 border-red-800/40 text-red-300',
    primary: 'from-indigo-950/60 to-slate-900/60 border-indigo-700/40 text-indigo-200',
  }[variant];
  return (
    <div
      className={`bg-gradient-to-br ${variantClass} border rounded-2xl p-6 backdrop-blur-sm`}
    >
      <div className="text-sm text-slate-400 mb-2">{label}</div>
      <div className="flex items-baseline gap-1">
        <span className="text-5xl md:text-6xl font-bold tracking-tight">
          {value}
        </span>
        <span className="text-2xl text-slate-400">{suffix}</span>
      </div>
      {sub && <div className="text-xs text-slate-500 mt-2">{sub}</div>}
    </div>
  );
}

function MiniCard({
  label,
  value,
  highlight,
}: {
  label: string;
  value: number;
  highlight?: 'success';
}) {
  const valueClass = highlight === 'success' ? 'text-emerald-400' : 'text-white';
  return (
    <div className="bg-slate-900/60 rounded-lg p-4 border border-slate-800">
      <div className="text-xs text-slate-400 mb-2 truncate">{label}</div>
      <div className={`text-3xl font-bold ${valueClass}`}>
        {value}
        <span className="text-sm text-slate-500 font-normal ml-1">件</span>
      </div>
    </div>
  );
}

function InfoCard({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: 'muted' | 'warning' | 'primary';
}) {
  const toneClass = {
    muted: 'text-slate-300',
    warning: 'text-amber-300',
    primary: 'text-sky-300',
  }[tone];
  return (
    <div className="bg-slate-900/60 rounded-lg p-4 border border-slate-800">
      <div className="text-xs text-slate-400 mb-2">{label}</div>
      <div className={`text-2xl font-bold font-mono ${toneClass}`}>{value}</div>
    </div>
  );
}
