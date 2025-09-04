-- Make created_by optional to support anonymous writes
alter table public.client_schools alter column created_by drop not null;

