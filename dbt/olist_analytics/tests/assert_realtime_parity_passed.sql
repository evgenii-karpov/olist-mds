{{ config(tags=['realtime_parity']) }}

select
    metric_name,
    status
from {{ ref('realtime_parity_report') }}
where status <> 'PASS'

union all

select
    metric_name,
    status
from {{ ref('realtime_parity_checksums') }}
where status <> 'PASS'

union all

select
    metric_name,
    'FAIL' as status
from {{ ref('realtime_parity_grain_diffs') }}
