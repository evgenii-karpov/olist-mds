{{ config(tags=['realtime_quality']) }}

with ranked as (
    select
        reconciliation.*,
        row_number() over (
            partition by reconciliation.source_table
            order by
                reconciliation.created_at desc,
                reconciliation.reconciliation_id desc
        ) as row_number
    from {{ source('cdc_audit', 'cdc_reconciliation') }} as reconciliation
)

select *
from ranked
where row_number = 1 and status <> 'PASS'
