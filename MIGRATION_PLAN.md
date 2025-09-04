## Migration Plan: Streamlit -> Next.js (App Router, TS) + Supabase

### 1) Current App Inventory (as-is)
- Entry point: `app.py` (Streamlit multipage overview dashboard)
- Additional Streamlit pages:
  - `pages/1_🗺️_Map.py` — Folium map, filters, clients-only toggle
  - `pages/2_🎯_Clients.py` — Client management (mark/unmark)
- Shared utilities:
  - `lib/config.py` — constants (columns, file names, level filters)
  - `lib/data.py` — CSV loading, client persistence to `client_schools.json` (with optional GitHub backing), dataframe transforms, toggle client
  - `lib/maps.py` — Folium map utilities
- Data files (CSV; at least one expected in repo/workspace):
  - `nl_highschools_accurate_coordinates.csv` (preferred)
  - `nl_highschools_with_coordinates.csv` (fallback)
  - `nl_highschools_full.csv` (raw)
- Persisted client IDs: `client_schools.json` (optionally mirrored to GitHub via token)
- Python deps: `requirements.txt` (streamlit, plotly, folium, pandas, etc.)

Key UX/logic
- Sidebar filters: province, relevant levels [VMBO, HAVO, VWO], size, denomination
- The memory constraint: hide PRO, BRUGJAAR, MAVO from filters (but keep schools if they also offer other levels). Already implemented in lib.data via IRRELEVANT_LEVELS.
- Tabs: Overview (metrics + charts), Geographic (map + city histogram), Education (level breakdown), Contact (website/phone stats), School Finder (search + toggle client)
- Client set toggling updates `client_schools.json` and optionally pushes to GitHub

### 2) Target Stack/Architecture
- Next.js 14+ App Router, TypeScript strict
- Tailwind CSS + shadcn/ui for UI primitives
- Supabase: Postgres, Auth, Storage (placeholder), SSR helpers; RLS on app tables
- Charts: Recharts (client-only components)
- Map: react-leaflet (client-only) with clustering
- Data access: Supabase from Server Components, server actions for mutations, route handlers under `app/api/*` when needed

### 3) Supabase Data Model (Postgres)
Tables
- schools (imported from CSV)
  - id text primary key (DUO vestigings_id)
  - school_name text not null
  - city text
  - province text
  - latitude double precision
  - longitude double precision
  - website text
  - phone_formatted text
  - has_website boolean
  - education_structure text
  - levels_offered text
  - vmbo boolean
  - havo boolean
  - vwo boolean
  - pro boolean
  - mavo boolean
  - brugjaar boolean
  - enrollment_total integer
  - school_size_category text
  - denomination text
  - created_at timestamptz default now()

- client_schools
  - school_id text references schools(id) on delete cascade
  - owner uuid references auth.users(id) not null
  - created_at timestamptz default now()
  - primary key (school_id, owner)

Indexes
- schools(city), schools(province)
- client_schools(owner)

RLS
- schools: read-only to authenticated users
  - enable RLS; policy: authenticated can select
- client_schools: per-user ownership
  - enable RLS; policies: select/insert/delete where owner = auth.uid()
  - optionally: add an "org" model later if team sharing is desired

Initial migration file: `supabase/migrations/0001_init.sql` implementing above + RLS

### 4) Data Migration from CSV
- Seed pipeline will read the best-available CSV (`accurate` > `with_coordinates` > `full`), normalize column names to the expected schema, and bulk insert into `schools`.
- Implementation options:
  - scripts/seed.ts (Node) using `pg` with `DATABASE_URL` or using Supabase client with `SUPABASE_SERVICE_ROLE_KEY` for batch upserts
  - or Supabase CLI `seed.sql` — less flexible for CSV parsing; we’ll provide the TS script.
- Idempotency: upsert on `schools.id`.

### 5) App Routes and Feature Parity
- app/(public)/landing/page.tsx — marketing/landing (public)
- app/(dashboard)/layout.tsx — shell with sidebar filters (persist in search params)
- app/(dashboard)/page.tsx — Overview: KPIs + charts
- app/(dashboard)/map/page.tsx — Map with filters (province, search, clients-only)
- app/(dashboard)/clients/page.tsx — Client management list with search + toggle
- app/auth/sign-in/page.tsx — Email/password + OAuth placeholders
- app/auth/callback/route.ts — Supabase auth route handling

Mapping notes
- Sidebar filters -> controlled components; persist in URL search params
- Tables -> shadcn table components with server-side pagination
- Charts -> client components (Recharts) fed by server-fetched data
- Clients toggle -> server action mutating `client_schools` (insert/delete)
- Session state -> Supabase Auth session; filters in URL
- Exclude PRO, BRUGJAAR, MAVO from filter options but keep in DB; do not display in levels filter or chips

### 6) Supabase Clients (Next.js)
- lib/supabase/server.ts — SSR client from cookies (anon key)
- lib/supabase/client.ts — browser client (anon key)
- For seeds/admin: use `SUPABASE_SERVICE_ROLE_KEY` only in server-only contexts (scripts, route handlers)

### 7) Auth and Protection
- middleware.ts protecting `(dashboard)` group: require authenticated session
- Public routes: landing, auth
- On sign-in success -> redirect to `/`

### 8) Tooling and DX
- Tailwind config + globals
- shadcn/ui init; generate Button, Input, Select, Label, Table, Card, Dialog, Tabs, Toaster
- ESLint + Prettier
- Tests: minimal Vitest smoke test for rendering homepage; optionally Playwright later
- .env.example containing
  - NEXT_PUBLIC_SUPABASE_URL
  - NEXT_PUBLIC_SUPABASE_ANON_KEY
  - SUPABASE_SERVICE_ROLE_KEY
  - (optional) DATABASE_URL for direct `pg` seeding

### 9) Cleanup Plan
- Remove Streamlit app (`app.py`, `pages/**`, `.streamlit/**`) and Python-only deps (`requirements.txt`) after Next app verified running
- Retain CSV building scripts for data generation (optional), but mark as legacy in README

### 10) Phased Execution
1. Scaffold Next app in `/web` (to keep root clean during transition)
   - Next.js (TS), Tailwind, shadcn/ui
   - Install deps: `@supabase/supabase-js @supabase/ssr zod lucide-react class-variance-authority tailwind-merge react-leaflet leaflet recharts vitest @testing-library/react @testing-library/jest-dom` 
2. Add Supabase clients, auth pages, middleware
3. Create migrations (0001) and commit
4. Implement queries and server actions for filters, KPIs, clients toggle
5. Implement Overview, Map, Clients pages with parity
6. Seed schools from CSV via `scripts/seed.ts`
7. Smoke test, update README, prune Streamlit code

### 11) Open Questions / Assumptions
- Multi-user semantics for clients: initial implementation is per-user client set; if a shared team list is desired, we can add an "orgs" table and policies.
- Maps: react-leaflet is proposed; confirm acceptable. Alternative: MapLibre GL.
- Deployment target? (Vercel + Supabase recommended)

### 12) Acceptance Targets
- `pnpm i && pnpm dev` serves landing and dashboard without runtime errors
- Supabase Auth functional; protected routes enforced
- RLS blocks cross-user client access
- README documents env, migrations, seeds, and run flow

