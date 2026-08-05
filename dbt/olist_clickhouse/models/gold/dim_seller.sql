{{
    config(
        materialized='incremental',
        incremental_strategy='insert_overwrite',
        engine='MergeTree()',
        partition_by='sync_run_seq',
        order_by=['seller_id'],
        post_hook="{{ create_or_replace_gold_view() }}"
    )
}}
{{ require_run_context() }}

SELECT
    {{ candidate_run_columns() }},
    lower(hex(MD5(seller_id))) AS seller_key,
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
FROM {{ ref('stg_sellers_current') }}
