{{ config(tags=['realtime_quality']) }}

select *
from {{ source('cdc_audit', 'cdc_partition_watermarks') }}
where gap_count <> 0
