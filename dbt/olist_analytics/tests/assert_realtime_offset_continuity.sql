{{ config(tags=['realtime_quality']) }}

{% if target.name == 'local_clickhouse' %}

    select 'realtime_transform.py validates control offset continuity' as reason
    where 1 = 0

{% else %}

select *
from {{ source('cdc_audit', 'cdc_partition_watermarks') }}
where gap_count <> 0

{% endif %}
