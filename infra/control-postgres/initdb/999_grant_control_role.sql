grant usage on schema audit to :"control_user";
grant usage on schema cdc_audit to :"control_user";

grant select, insert, update, delete on all tables in schema audit to :"control_user";
grant select, insert, update, delete on all tables in schema cdc_audit to :"control_user";
grant usage, select on all sequences in schema audit to :"control_user";
grant usage, select on all sequences in schema cdc_audit to :"control_user";

alter default privileges in schema audit
    grant select, insert, update, delete on tables to :"control_user";
alter default privileges in schema cdc_audit
    grant select, insert, update, delete on tables to :"control_user";
alter default privileges in schema audit
    grant usage, select on sequences to :"control_user";
alter default privileges in schema cdc_audit
    grant usage, select on sequences to :"control_user";
