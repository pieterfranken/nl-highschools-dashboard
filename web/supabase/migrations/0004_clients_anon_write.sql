-- Allow anonymous insert/delete on client_schools for public use (no auth required)
-- This is acceptable if clients list is intended to be public-write. Consider rate limiting at edge if needed.
create policy "anon insert clients" on public.client_schools for insert with check (true);
create policy "anon delete clients" on public.client_schools for delete using (true);

