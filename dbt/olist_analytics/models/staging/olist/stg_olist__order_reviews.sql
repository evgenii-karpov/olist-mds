with ranked as (
    select
        {{ cast_string('review_id', 256) }} as review_id,
        {{ cast_string('order_id', 256) }} as order_id,
        {{ cast_int('review_score') }} as review_score,
        {{ cast_string("nullif(trim(review_comment_title), '')", 1024) }}
            as review_comment_title,
        {{ cast_string("nullif(trim(review_comment_message), '')", 65535) }}
            as review_comment_message,
        {{ cast_timestamp('review_creation_date') }} as review_creation_date,
        {{ cast_timestamp('review_answer_timestamp') }}
            as review_answer_timestamp,
        _batch_id,
        _loaded_at,
        _source_file,
        _source_system,
        row_number() over (
            partition by review_id, order_id
            order by _loaded_at desc, _batch_id desc
        ) as row_number
    from {{ source('olist', 'order_reviews') }}
)

select
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,
    review_creation_date,
    review_answer_timestamp,
    _batch_id,
    _loaded_at,
    _source_file,
    _source_system
from ranked
where row_number = 1
