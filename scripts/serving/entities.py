"""Serving entity specifications and unified registry."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ServingEntitySpec:
    entity: str
    primary_key: tuple[str, ...]
    source_topic: str
    changes_relation: str
    ch_events_table: str
    ch_current_versions_table: str
    ch_current_view: str
    business_columns: tuple[str, ...]


ALL_SERVING_ENTITIES: tuple[ServingEntitySpec, ...] = (
    ServingEntitySpec(
        entity="customers",
        primary_key=("customer_id",),
        source_topic="olist.olist_oltp.customers",
        changes_relation="lakehouse.silver.customers_changes",
        ch_events_table="serving_cdc.customers_events",
        ch_current_versions_table="serving_cdc.customers_current_versions",
        ch_current_view="serving_cdc.customers_current",
        business_columns=(
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state",
        ),
    ),
    ServingEntitySpec(
        entity="orders",
        primary_key=("order_id",),
        source_topic="olist.olist_oltp.orders",
        changes_relation="lakehouse.silver.orders_changes",
        ch_events_table="serving_cdc.orders_events",
        ch_current_versions_table="serving_cdc.orders_current_versions",
        ch_current_view="serving_cdc.orders_current",
        business_columns=(
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ),
    ),
    ServingEntitySpec(
        entity="order_items",
        primary_key=("order_id", "order_item_id"),
        source_topic="olist.olist_oltp.order_items",
        changes_relation="lakehouse.silver.order_items_changes",
        ch_events_table="serving_cdc.order_items_events",
        ch_current_versions_table="serving_cdc.order_items_current_versions",
        ch_current_view="serving_cdc.order_items_current",
        business_columns=(
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value",
        ),
    ),
    ServingEntitySpec(
        entity="order_payments",
        primary_key=("order_id", "payment_sequential"),
        source_topic="olist.olist_oltp.order_payments",
        changes_relation="lakehouse.silver.order_payments_changes",
        ch_events_table="serving_cdc.order_payments_events",
        ch_current_versions_table="serving_cdc.order_payments_current_versions",
        ch_current_view="serving_cdc.order_payments_current",
        business_columns=(
            "payment_type",
            "payment_installments",
            "payment_value",
        ),
    ),
    ServingEntitySpec(
        entity="order_reviews",
        primary_key=("review_id",),
        source_topic="olist.olist_oltp.order_reviews",
        changes_relation="lakehouse.silver.order_reviews_changes",
        ch_events_table="serving_cdc.order_reviews_events",
        ch_current_versions_table="serving_cdc.order_reviews_current_versions",
        ch_current_view="serving_cdc.order_reviews_current",
        business_columns=(
            "order_id",
            "review_score",
            "review_comment_title",
            "review_comment_message",
            "review_creation_date",
            "review_answer_timestamp",
        ),
    ),
    ServingEntitySpec(
        entity="products",
        primary_key=("product_id",),
        source_topic="olist.olist_oltp.products",
        changes_relation="lakehouse.silver.products_changes",
        ch_events_table="serving_cdc.products_events",
        ch_current_versions_table="serving_cdc.products_current_versions",
        ch_current_view="serving_cdc.products_current",
        business_columns=(
            "product_category_name",
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ),
    ),
    ServingEntitySpec(
        entity="sellers",
        primary_key=("seller_id",),
        source_topic="olist.olist_oltp.sellers",
        changes_relation="lakehouse.silver.sellers_changes",
        ch_events_table="serving_cdc.sellers_events",
        ch_current_versions_table="serving_cdc.sellers_current_versions",
        ch_current_view="serving_cdc.sellers_current",
        business_columns=(
            "seller_zip_code_prefix",
            "seller_city",
            "seller_state",
        ),
    ),
    ServingEntitySpec(
        entity="product_category_translation",
        primary_key=("product_category_name",),
        source_topic="olist.olist_oltp.product_category_translation",
        changes_relation="lakehouse.silver.product_category_translation_changes",
        ch_events_table="serving_cdc.product_category_translation_events",
        ch_current_versions_table="serving_cdc.product_category_translation_current_versions",
        ch_current_view="serving_cdc.product_category_translation_current",
        business_columns=("product_category_name_english",),
    ),
)

_ENTITY_INDEX = {spec.entity: spec for spec in ALL_SERVING_ENTITIES}


def get_entity_spec(entity: str) -> ServingEntitySpec:
    if entity not in _ENTITY_INDEX:
        raise KeyError(f"Unknown serving entity: {entity}")
    return _ENTITY_INDEX[entity]
