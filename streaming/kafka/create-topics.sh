#!/usr/bin/env bash
set -euo pipefail

bootstrap_server="${1:-kafka:29092}"
kafka_topics=/opt/kafka/bin/kafka-topics.sh

create_topic() {
  local name="$1" partitions="$2" cleanup="$3" retention="$4"
  "$kafka_topics" --bootstrap-server "$bootstrap_server" --create --if-not-exists \
    --topic "$name" --partitions "$partitions" --replication-factor 1 \
    --config "cleanup.policy=$cleanup" --config "retention.ms=$retention"
}

create_topic olist_connect_configs 1 compact -1
create_topic olist_connect_offsets 25 compact -1
create_topic olist_connect_status 5 compact -1
create_topic olist_cdc.schema_history 1 compact -1
create_topic olist_cdc.transaction 1 delete 604800000
create_topic olist_cdc.heartbeat 1 delete 604800000

create_topic olist_cdc.public.customers 1 delete 604800000
create_topic olist_cdc.public.orders 3 delete 604800000
create_topic olist_cdc.public.order_items 3 delete 604800000
create_topic olist_cdc.public.order_payments 3 delete 604800000
create_topic olist_cdc.public.order_reviews 3 delete 604800000
create_topic olist_cdc.public.products 1 delete 604800000
create_topic olist_cdc.public.sellers 1 delete 604800000
create_topic olist_cdc.public.product_category_translation 1 delete 604800000

create_topic olist_cdc.dlq.customers 1 delete 604800000
create_topic olist_cdc.dlq.orders 3 delete 604800000
create_topic olist_cdc.dlq.order_items 3 delete 604800000
create_topic olist_cdc.dlq.order_payments 3 delete 604800000
create_topic olist_cdc.dlq.order_reviews 3 delete 604800000
create_topic olist_cdc.dlq.products 1 delete 604800000
create_topic olist_cdc.dlq.sellers 1 delete 604800000
create_topic olist_cdc.dlq.product_category_translation 1 delete 604800000
