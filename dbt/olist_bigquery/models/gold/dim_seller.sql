{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key=['sync_run_seq', 'operation_type', 'seller_id'],
        alias='dim_seller__history',
        partition_by={
            'field': 'built_at',
            'data_type': 'timestamp',
            'granularity': 'day'
        },
        cluster_by=['sync_run_seq', 'seller_id'],
        pre_hook="{{ delete_same_run_history(this) }}"
    )
}}
{{ require_run_context() }}

SELECT
    {{ history_columns(
        "CASE WHEN is_deleted THEN 'DELETE' ELSE 'UPSERT' END"
    ) }},
    LOWER(TO_HEX(MD5(seller_id))) AS seller_key,
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
FROM {{ ref('stg_sellers_current') }}
