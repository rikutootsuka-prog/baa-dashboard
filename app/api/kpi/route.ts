import { NextResponse } from 'next/server';
import { getKPI } from '@/lib/kpi';

export const dynamic = 'force-dynamic';
export const revalidate = 60;

export async function GET() {
  try {
    const kpi = await getKPI();
    return NextResponse.json(kpi, {
      headers: {
        'Cache-Control': 's-maxage=60, stale-while-revalidate=300',
      },
    });
  } catch (err) {
    console.error('KPI fetch error:', err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
