import { fetchSheetValues } from './sheets';

const SHEET_ID = '1fJlu1Ky2rNS3GepLGH2PUajE88kNzk9eqWGMf4m53aI';
const DASHBOARD_RANGE = 'BAA経営ダッシュボード!A1:C32';
export const SHEET_URL = `https://docs.google.com/spreadsheets/d/${SHEET_ID}/edit?gid=1573501633`;

export interface KPI {
  lastUpdated: string;
  targetMonth: string;
  sales: {
    apoTotal: number;
    juchu: number;
    bYomi: number;
    cPlus: number;
    cMinus: number;
    dYomi: number;
    kurikoshi: number;
  };
  forecast: {
    target: number;
    achieved: number;
    bYomi: number;
    remaining: number;
    progress: number;
  };
  required: {
    rate: number;
    standardApo: number;
  };
  deadline: {
    monthEnd: string;
    apoDeadline: string;
    daysLeft: number;
  };
  alerts: {
    phaseUnset: number;
  };
}

const WEEKDAYS = ['日', '月', '火', '水', '木', '金', '土'];

function serialToDate(serial: number): string {
  if (!serial || isNaN(serial)) return '—';
  const date = new Date(Date.UTC(1899, 11, 30) + serial * 86400000);
  const yyyy = date.getUTCFullYear();
  const mm = date.getUTCMonth() + 1;
  const dd = date.getUTCDate();
  const w = WEEKDAYS[date.getUTCDay()];
  return `${yyyy}/${mm}/${dd}(${w})`;
}

function toNumber(v: unknown, defaultValue = 0): number {
  if (typeof v === 'number') return v;
  if (typeof v === 'string') {
    const n = Number(v);
    return isNaN(n) ? defaultValue : n;
  }
  return defaultValue;
}

function toString(v: unknown, defaultValue = ''): string {
  return v === null || v === undefined ? defaultValue : String(v);
}

export async function getKPI(): Promise<KPI> {
  const values = await fetchSheetValues(SHEET_ID, DASHBOARD_RANGE);
  const dict: Record<string, unknown> = {};
  for (const row of values) {
    if (!row || !row[0]) continue;
    const key = String(row[0]).trim();
    if (key) dict[key] = row[1];
  }

  return {
    lastUpdated: toString(dict['最終更新']),
    targetMonth: toString(dict['対象月']),
    sales: {
      apoTotal: toNumber(dict['月内アポ実施数']),
      juchu: toNumber(dict['当月受注数 (Jヨミ)']),
      bYomi: toNumber(dict['Bヨミ']),
      cPlus: toNumber(dict['Cヨミ+']),
      cMinus: toNumber(dict['Cヨミ−']),
      dYomi: toNumber(dict['Dヨミ']),
      kurikoshi: toNumber(dict['繰越数 (先月以前アポ・未結着)']),
    },
    forecast: {
      target: toNumber(dict['受注社数目標']),
      achieved: toNumber(dict['当月受注実績']),
      bYomi: toNumber(dict['Bヨミ社数']),
      remaining: toNumber(dict['実質残必要受注']),
      progress: toNumber(dict['進捗率']),
    },
    required: {
      rate: toNumber(dict['想定受注率 (固定)'], 0.34),
      standardApo: toNumber(dict['標準 残必要アポ']),
    },
    deadline: {
      monthEnd: serialToDate(toNumber(dict['月末日'])),
      apoDeadline: serialToDate(toNumber(dict['アポ取得締切 (5営業日前)'])),
      daysLeft: toNumber(dict['締切まで残営業日']),
    },
    alerts: {
      phaseUnset: toNumber(dict['当月フェーズ未判定件数']),
    },
  };
}
