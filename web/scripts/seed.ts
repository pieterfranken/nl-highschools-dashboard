/*
  Seed script: imports the best available CSV into public.schools
  Usage: SUPABASE_SERVICE_ROLE_KEY=... NEXT_PUBLIC_SUPABASE_URL=... pnpm tsx scripts/seed.ts
*/
import fs from 'node:fs';
import path from 'node:path';
import { parse } from 'csv-parse';
import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY!;

if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
  console.error('Missing env: NEXT_PUBLIC_SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY');
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

const candidates = [
  'nl_highschools_accurate_coordinates.csv',
  'nl_highschools_with_coordinates.csv',
  'nl_highschools_full.csv',
];

function pickCsv(): string | null {
  for (const f of candidates) {
    const p = path.resolve(process.cwd(), '..', f);
    if (fs.existsSync(p)) return p;
  }
  return null;
}

function toBool(v: any): boolean | null {
  if (v === undefined || v === null || v === '') return null;
  if (typeof v === 'boolean') return v;
  const s = String(v).toLowerCase();
  if (['1', 'true', 'yes', 'y'].includes(s)) return true;
  if (['0', 'false', 'no', 'n'].includes(s)) return false;
  return null;
}

async function run() {
  const csvPath = pickCsv();
  if (!csvPath) {
    console.error('No CSV found next to repo root');
    process.exit(1);
  }
  console.log('Using CSV:', csvPath);

  const parser = fs
    .createReadStream(csvPath)
    .pipe(parse({ columns: true, bom: true, skip_empty_lines: true }));

  const batch: any[] = [];
  let count = 0;
  for await (const row of parser) {
    const record = {
      id: String(row['vestigings_id'] ?? row['id'] ?? ''),
      school_name: row['school_name'] ?? row['name'] ?? null,
      city: row['city'] ?? null,
      province: row['province'] ?? null,
      latitude: row['latitude'] ? Number(row['latitude']) : null,
      longitude: row['longitude'] ? Number(row['longitude']) : null,
      website: row['website'] ?? null,
      phone_formatted: row['phone_formatted'] ?? row['phone'] ?? null,
      has_website: toBool(row['has_website']),
      education_structure: row['education_structure'] ?? null,
      levels_offered: row['levels_offered'] ?? null,
      vmbo: toBool(row['VMBO']),
      havo: toBool(row['HAVO']),
      vwo: toBool(row['VWO']),
      pro: toBool(row['PRO']),
      mavo: toBool(row['MAVO']),
      brugjaar: toBool(row['BRUGJAAR']),
      enrollment_total: row['enrollment_total'] ? Number(row['enrollment_total']) : null,
      school_size_category: row['school_size_category'] ?? null,
      denomination: row['denomination'] ?? null,
    };
    if (!record.id) continue;
    batch.push(record);

    if (batch.length >= 500) {
      const { error } = await supabase.from('schools').upsert(batch, { onConflict: 'id' });
      if (error) throw error;
      count += batch.length;
      batch.length = 0;
      process.stdout.write(`Upserted ${count}\r`);
    }
  }
  if (batch.length) {
    const { error } = await supabase.from('schools').upsert(batch, { onConflict: 'id' });
    if (error) throw error;
    count += batch.length;
  }
  console.log(`\nDone. Total upserted: ${count}`);
}

run().catch((e) => {
  console.error(e);
  process.exit(1);
});

