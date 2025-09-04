# NL Highschools Web (Next.js + Supabase)

This is the Next.js (App Router, TypeScript) migration of the Streamlit app.

## Prerequisites
- Node 18+ and pnpm installed
- A Supabase project (URL + anon key + service role key)

## Setup
1. Copy env
```bash
cp .env.example .env.local
# Fill in NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY
```
2. Install deps
```bash
pnpm install
```
3. Run dev
```bash
pnpm dev
```

## Database
Run the migration SQL in your Supabase project (via Supabase SQL editor or CLI):
- `supabase/migrations/0001_init.sql`

Then seed from the CSVs in the repo root (it picks the best available):
```bash
NEXT_PUBLIC_SUPABASE_URL=... \
SUPABASE_SERVICE_ROLE_KEY=... \
pnpm dlx tsx scripts/seed.ts
```

## Notes
- Client schools are shared across authenticated users (audit via created_by, created_at)
- We keep PRO/BRUGJAAR/MAVO in the DB but exclude from filter UI (to be implemented in UI)

