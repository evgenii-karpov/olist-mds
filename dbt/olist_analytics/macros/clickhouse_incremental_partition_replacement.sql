{% macro fact_order_items_purchase_partition_id(expression) -%}
    toString(toYYYYMM(coalesce(toDate({{ expression }}), toDate('1900-01-01'))))
{%- endmacro %}

{% macro fact_order_items_affected_partitions_relation() -%}
    {{ this.schema }}.{{ this.identifier }}__affected_partitions
{%- endmacro %}

{% macro clickhouse_drop_fact_order_items_affected_partitions() -%}
    {% if target.type == 'clickhouse' %}
        drop table if exists {{ fact_order_items_affected_partitions_relation() }}
    {% else %}
        select 1
    {% endif %}
{%- endmacro %}

{% macro clickhouse_prepare_fact_order_items_affected_partitions() -%}
    {% if target.type == 'clickhouse' and is_incremental() %}
        create table {{ fact_order_items_affected_partitions_relation() }}
        engine = Memory
        as
        {{ fact_order_items_affected_partitions_sql(this) }}
    {% else %}
        select 1
    {% endif %}
{%- endmacro %}

{% macro fact_order_items_affected_partitions_sql(existing_relation) -%}
with

source_orders as (
    select *
    from {{ ref('stg_olist__orders') }}
),

source_order_items as (
    select *
    from {{ ref('stg_olist__order_items') }}
),

source_items as (
    select
        {{
            hash_key(
                "source_order_items.order_id || '|' || "
                ~ cast_string('source_order_items.order_item_id')
            )
        }} as order_item_key,
        source_orders.order_purchase_timestamp as source_order_purchase_timestamp,
        {{ fact_order_items_purchase_partition_id('source_orders.order_purchase_timestamp') }}
            as source_partition_id
    from source_order_items
    inner join source_orders
        on source_order_items.order_id = source_orders.order_id
),

existing_items as (
    select
        order_item_key,
        {{ fact_order_items_purchase_partition_id('order_purchase_timestamp') }}
            as existing_partition_id,
        order_purchase_timestamp as existing_order_purchase_timestamp
    from {{ existing_relation }}
),

lookback_boundary as (
    select
        coalesce(
        {{ dateadd_days(
            'max(existing_order_purchase_timestamp)',
            var('lookback_days', 3) | int * -1
        ) }},
            {{ timestamp_literal('1900-01-01') }}
        ) as reprocess_from
    from existing_items
),

correction_boundary as (
    select min(effective_at) as reprocess_from
    from (
        select effective_at
        from {{ ref('stg_olist__customer_profile_changes') }}

        union all

        select effective_at
        from {{ ref('stg_olist__product_attribute_changes') }}
    ) as correction_events
),

boundary_partitions as (
    select distinct source_partition_id as partition_id
    from source_items
    where source_order_purchase_timestamp >= (
        select reprocess_from
        from lookback_boundary
    )

    union distinct

    select distinct source_partition_id as partition_id
    from source_items
    where source_order_purchase_timestamp >= (
        select reprocess_from
        from correction_boundary
    )
),

new_partitions as (
    select distinct source_partition_id as partition_id
    from source_items
    where
        order_item_key not in (
            select order_item_key
            from existing_items
            where order_item_key is not null
        )
),

deleted_or_moved_partitions as (
    select distinct existing_partition_id as partition_id
    from existing_items
    where
        order_item_key not in (
            select order_item_key
            from source_items
            where order_item_key is not null
        )

    union distinct

    select distinct source_items.source_partition_id as partition_id
    from existing_items
    inner join source_items
        on existing_items.order_item_key = source_items.order_item_key
    where source_items.source_partition_id != existing_items.existing_partition_id
)

select partition_id
from boundary_partitions
where partition_id is not null

union distinct

select partition_id
from new_partitions
where partition_id is not null

union distinct

select partition_id
from deleted_or_moved_partitions
where partition_id is not null
{%- endmacro %}

{% macro clickhouse__incremental_insert_overwrite(existing_relation, partition_by, is_distributed=False) %}
    {% set new_data_relation = existing_relation.incorporate(path={"identifier": existing_relation.identifier
       + '__dbt_new_data_' + invocation_id.replace('-', '_')}) %}
    {{ drop_relation_if_exists(new_data_relation) }}
    {%- set distributed_new_data_relation = existing_relation.incorporate(path={"identifier": existing_relation.identifier + '__dbt_distributed_new_data'}) -%}

    {%- set local_suffix = adapter.get_clickhouse_local_suffix() -%}
    {%- set local_db_prefix = adapter.get_clickhouse_local_db_prefix() -%}
    {% set existing_local = existing_relation.incorporate(path={"identifier": this.identifier + local_suffix, "schema": local_db_prefix + this.schema}) if existing_relation is not none else none %}
    {% set affected_partitions_relation = existing_relation.incorporate(path={"identifier": existing_relation.identifier + '__affected_partitions'}) %}

    {% if is_distributed %}
        {{ create_distributed_local_table(distributed_new_data_relation, new_data_relation, existing_relation, sql) }}
    {% else %}
        {% call statement('main') %}
            {{ get_create_table_as_sql(False, new_data_relation, sql) }}
        {% endcall %}
    {% endif %}

    {% if execute %}
        {% set select_changed_partitions %}
            select distinct partition_id
            {% if is_distributed %}
                from cluster({{ adapter.get_clickhouse_cluster_name() }}, system.parts)
            {% else %}
                from system.parts
            {% endif %}
            where active
                and database = '{{ new_data_relation.schema }}'
                and table = '{{ new_data_relation.identifier }}'
        {% endset %}
        {% set changed_partitions = run_query(select_changed_partitions).rows %}

        {% set select_partitions_to_drop %}
            with
            changed_partitions as (
                select distinct partition_id
                {% if is_distributed %}
                    from cluster({{ adapter.get_clickhouse_cluster_name() }}, system.parts)
                {% else %}
                    from system.parts
                {% endif %}
                where active
                    and database = '{{ new_data_relation.schema }}'
                    and table = '{{ new_data_relation.identifier }}'
            ),
            target_partitions as (
                select distinct partition_id
                {% if is_distributed %}
                    from cluster({{ adapter.get_clickhouse_cluster_name() }}, system.parts)
                {% else %}
                    from system.parts
                {% endif %}
                where active
                    and database = '{{ existing_relation.schema }}'
                    and table = '{{ existing_relation.identifier }}'
            )
            select distinct affected.partition_id
            from {{ affected_partitions_relation }} as affected
            inner join target_partitions
                on affected.partition_id = target_partitions.partition_id
            where
                affected.partition_id not in (
                    select partition_id
                    from changed_partitions
                    where partition_id != ''
                )
        {% endset %}
        {% set partitions_to_drop = run_query(select_partitions_to_drop).rows %}
    {% else %}
        {% set changed_partitions = [] %}
        {% set partitions_to_drop = [] %}
    {% endif %}

    {% for partition in changed_partitions %}
        {% if partition['partition_id'] %}
            {% call statement('replace_partition_' ~ loop.index) %}
            {% if is_distributed %}
                alter table {{ existing_local }} {{ on_cluster_clause(existing_relation) }}
            {% else %}
                alter table {{ existing_relation }}
            {% endif %}
            replace partition id '{{ partition['partition_id'] }}'
            from {{ new_data_relation }}
            {% endcall %}
        {% endif %}
    {% endfor %}

    {% for partition in partitions_to_drop %}
        {% if partition['partition_id'] %}
            {% call statement('drop_empty_partition_' ~ loop.index) %}
            {% if is_distributed %}
                alter table {{ existing_local }} {{ on_cluster_clause(existing_relation) }}
            {% else %}
                alter table {{ existing_relation }}
            {% endif %}
            drop partition id '{{ partition['partition_id'] }}'
            {% endcall %}
        {% endif %}
    {% endfor %}

    {% do adapter.drop_relation(distributed_new_data_relation) %}
    {% do adapter.drop_relation(new_data_relation) %}
    {{ drop_relation_if_exists(affected_partitions_relation) }}
{% endmacro %}
