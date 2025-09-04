-- Allow anonymous (public) read access to schools for initial testing and public map
create policy "anon read schools" on public.schools for select using (true);

