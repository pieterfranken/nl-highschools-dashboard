# Streamlit to Next.js + Supabase Migration

This repo is being migrated from Streamlit to a Next.js App Router + Supabase stack. New app lives under `/web`.

## Quick start
- Ensure Node 18+ and pnpm are installed
- cd web && cp .env.example .env.local && fill Supabase keys
- pnpm install && pnpm dev
- Apply `web/supabase/migrations/0001_init.sql` in Supabase
- Seed via `pnpm dlx tsx scripts/seed.ts`

## Parity mapping
- Overview KPIs/charts -> /(dashboard)/page.tsx + Recharts (coming)
- Map (clients highlighted) -> /(dashboard)/map
- Manage clients -> /(dashboard)/clients (server actions)
- Filters: province/levels/size/denomination/search; exclude PRO/BRUGJAAR/MAVO from UI

## Cleanup plan
- Once the Next app runs end-to-end, delete Streamlit files and Python UI deps

