-- Dedicated pipeline control schemas in PostgreSQL olist_control.

create schema if not exists audit;
create schema if not exists cdc_audit;

grant usage, create on schema audit to :"control_user";
grant usage, create on schema cdc_audit to :"control_user";
