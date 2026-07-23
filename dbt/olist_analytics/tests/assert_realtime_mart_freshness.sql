{{ config(tags=['realtime_quality']) }}

{% if target.name == 'local_clickhouse' %}

    select 'realtime_transform.py validates control mart freshness' as reason
    where 1 = 0

{% else %}

with expected_models as (
    select 'mart_daily_revenue_realtime' as model_name
    union all
    select 'mart_monthly_arpu_realtime' as model_name
),

raw_horizon as (
    select
        max(source_ts_max) as max_source_ts,
        max(loaded_at) as max_loaded_at
    from {{ source('cdc_audit', 'cdc_files') }}
    where status = 'LOADED'
)

select
    expected_models.model_name,
    freshness.max_source_ts,
    freshness.build_time
from expected_models
cross join raw_horizon
left join {{ source('cdc_audit', 'cdc_mart_freshness') }} as freshness
    on expected_models.model_name = freshness.model_name
where
    freshness.model_name is null
    or freshness.max_source_ts is null
    or freshness.build_time is null
    or (
        freshness.build_time < raw_horizon.max_loaded_at
        and extract(epoch from current_timestamp - raw_horizon.max_loaded_at)
        > {{ var('realtime_freshness_slo_seconds', 300) }}
    )

{% endif %}
    or (
        freshness.max_source_ts < raw_horizon.max_source_ts
        and extract(epoch from current_timestamp - raw_horizon.max_loaded_at)
        > {{ var('realtime_freshness_slo_seconds', 300) }}
    )
