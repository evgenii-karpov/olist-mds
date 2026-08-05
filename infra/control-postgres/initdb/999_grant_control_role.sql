-- Least-privilege grants for the target serving control schema.

grant usage, create on schema serving to :"control_user";
grant select, insert, update, delete on all tables in schema serving to :"control_user";
grant usage, select on all sequences in schema serving to :"control_user";

alter default privileges in schema serving
    grant select, insert, update, delete on tables to :"control_user";
alter default privileges in schema serving
    grant usage, select on sequences to :"control_user";
