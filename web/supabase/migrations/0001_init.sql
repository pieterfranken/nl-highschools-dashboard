-- Schema: schools and client_schools (shared list across authenticated users)
create table if not exists public.schools (
  id text primary key, -- vestigings_id
  school_name text not null,
  city text,
  province text,
  latitude double precision,
  longitude double precision,
  website text,
  phone_formatted text,
  has_website boolean,
  education_structure text,
  levels_offered text,
  vmbo boolean,
  havo boolean,
  vwo boolean,
  pro boolean,
  mavo boolean,
  brugjaar boolean,
  enrollment_total integer,
  school_size_category text,
  denomination text,
  created_at timestamptz not null default now()
);

create index if not exists idx_schools_city on public.schools (city);
create index if not exists idx_schools_province on public.schools (province);

alter table public.schools enable row level security;
-- Authenticated users can read all schools
create policy "read schools" on public.schools for select using (auth.role() = 'authenticated');

create table if not exists public.client_schools (
  school_id text not null references public.schools(id) on delete cascade,
  created_by uuid not null references auth.users(id),
  created_at timestamptz not null default now(),
  constraint client_schools_pkey primary key (school_id)
);

alter table public.client_schools enable row level security;
-- Shared across authenticated users; allow read and write
create policy "read clients" on public.client_schools for select using (auth.role() = 'authenticated');
create policy "write clients" on public.client_schools for insert with check (auth.role() = 'authenticated');
create policy "delete clients" on public.client_schools for delete using (auth.role() = 'authenticated');

