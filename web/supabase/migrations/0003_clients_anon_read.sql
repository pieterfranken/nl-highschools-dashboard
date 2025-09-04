-- Allow anonymous read access to client_schools for rendering public map/client badges
create policy "anon read clients" on public.client_schools for select using (true);

