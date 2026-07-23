{{ config(tags=['batch_quality']) }}

{% if target.name in ['local_pg', 'local_clickhouse'] %}

select 'batch reconciliation is validated by scripts/quality/reconcile_batch.py' as reason
where 1 = 0

{% else %}

with reconciliation as (
    select status
    from {{ source('pipeline_audit', 'batch_reconciliation') }}
    where batch_id = '{{ var("batch_date") }}'
),

summary as (
    select
        count(*) as reconciliation_rows,
        sum(case when status = 'PASS' then 1 else 0 end) as passed_rows
    from reconciliation
)

select *
from summary
where
    reconciliation_rows = 0
    or passed_rows <> reconciliation_rows

{% endif %}
