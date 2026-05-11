import { google } from 'googleapis';
import { execSync } from 'child_process';

const GWS_CLI = '/Users/ootsukarikuto/.nvm/versions/node/v22.17.0/bin/gws';

export type SheetRow = (string | number | null)[];

export async function fetchSheetValues(
  spreadsheetId: string,
  range: string
): Promise<SheetRow[]> {
  if (process.env.GOOGLE_SHEETS_CREDENTIALS_BASE64) {
    return fetchViaServiceAccount(spreadsheetId, range);
  }
  if (process.env.NODE_ENV === 'development') {
    return fetchViaGwsCli(spreadsheetId, range);
  }
  throw new Error(
    'No authentication method available. Set GOOGLE_SHEETS_CREDENTIALS_BASE64.'
  );
}

function fetchViaGwsCli(spreadsheetId: string, range: string): SheetRow[] {
  const params = JSON.stringify({
    spreadsheetId,
    range,
    valueRenderOption: 'UNFORMATTED_VALUE',
  });
  const output = execSync(
    `${GWS_CLI} sheets spreadsheets values get --params '${params}'`,
    { encoding: 'utf-8', maxBuffer: 10 * 1024 * 1024 }
  );
  const data = JSON.parse(output);
  return (data.values || []) as SheetRow[];
}

async function fetchViaServiceAccount(
  spreadsheetId: string,
  range: string
): Promise<SheetRow[]> {
  const credentials = JSON.parse(
    Buffer.from(
      process.env.GOOGLE_SHEETS_CREDENTIALS_BASE64!,
      'base64'
    ).toString('utf-8')
  );
  const auth = new google.auth.GoogleAuth({
    credentials,
    scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
  });
  const client = await auth.getClient();
  const sheets = google.sheets({ version: 'v4', auth: client as never });
  const res = await sheets.spreadsheets.values.get({
    spreadsheetId,
    range,
    valueRenderOption: 'UNFORMATTED_VALUE',
  });
  return (res.data.values || []) as SheetRow[];
}
