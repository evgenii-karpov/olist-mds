{{
    config(
        materialized='incremental',
        unique_key='seller_id',
        incremental_strategy='merge',
        tags=['realtime_transform', 'realtime_quality']
    )
}}

select
    md5(seller_id) as seller_key,
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state,
    _source_ts,
    _source_lsn,
    _tx_order,
    _partition,
    _offset
from {{ ref('stg_cdc__sellers_current') }}
