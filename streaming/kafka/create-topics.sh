#!/usr/bin/env bash
set -euo pipefail

# Keep this bootstrap dependency-free so it can run in apache/kafka:4.3.1.
# tests/cdc_contracts/test_topics.py proves that every declaration below is
# identical to topics.json. Existing topic configuration is reconciled on each
# run; Kafka still rejects an impossible partition decrease.

bootstrap_server="${1:-kafka:29092}"
kafka_bin="${KAFKA_HOME:-/opt/kafka}/bin"
kafka_topics="${kafka_bin}/kafka-topics.sh"
kafka_configs="${kafka_bin}/kafka-configs.sh"
dangerous_configs=(
  cleanup.policy
  retention.ms
  retention.bytes
  delete.retention.ms
  min.cleanable.dirty.ratio
  min.compaction.lag.ms
  max.compaction.lag.ms
  segment.ms
  segment.bytes
  message.timestamp.type
  max.message.bytes
  min.insync.replicas
  unclean.leader.election.enable
)

is_dangerous_config() {
  local candidate="$1"
  local dangerous
  for dangerous in "${dangerous_configs[@]}"; do
    if [[ "$candidate" == "$dangerous" ]]; then
      return 0
    fi
  done
  return 1
}

is_accepted_broker_default() {
  local key="$1"
  local value="$2"
  [[ "$key" == "min.insync.replicas" && "$value" == "1" ]]
}

validate_existing_topic() {
  local name="$1"
  local expected_partitions="$2"
  shift 2
  local declared_configs=("$@")
  local description
  local actual_partitions
  local config_text
  local raw_config
  local current_configs=()
  local key
  local declared
  local is_declared

  description="$(
    "$kafka_topics" --bootstrap-server "$bootstrap_server" \
      --describe --topic "$name"
  )"
  if [[ "$description" =~ PartitionCount:[[:space:]]*([0-9]+) ]]; then
    actual_partitions="${BASH_REMATCH[1]}"
  else
    echo "Cannot determine partition count for $name" >&2
    return 1
  fi
  if [[ "$actual_partitions" != "$expected_partitions" ]]; then
    echo "$name partition drift: actual=$actual_partitions expected=$expected_partitions" >&2
    return 1
  fi

  config_text="${description#*Configs: }"
  config_text="${config_text%%$'\n'*}"
  IFS=',' read -r -a current_configs <<< "$config_text"
  for raw_config in "${current_configs[@]}"; do
    key="${raw_config%%=*}"
    key="${key#"${key%%[![:space:]]*}"}"
    key="${key%"${key##*[![:space:]]}"}"
    is_declared=false
    for declared in "${declared_configs[@]}"; do
      if [[ "${declared%%=*}" == "$key" ]]; then
        is_declared=true
        break
      fi
    done
    if is_dangerous_config "$key" && [[ "$is_declared" == false ]]; then
      if ! is_accepted_broker_default "$key" "${raw_config#*=}"; then
        echo "$name has dangerous unmanifested override: $key" >&2
        return 1
      fi
    fi
  done
}

create_topic() {
  local name="$1"
  local partitions="$2"
  shift 2
  local configs=("$@")
  local create_args=()
  local joined=""

  for config in "${configs[@]}"; do
    create_args+=(--config "$config")
    if [[ -n "$joined" ]]; then
      joined+=","
    fi
    joined+="$config"
  done

  "$kafka_topics" --bootstrap-server "$bootstrap_server" --create \
    --if-not-exists --topic "$name" --partitions "$partitions" \
    --replication-factor 1 "${create_args[@]}"

  # --create --if-not-exists neither repairs partition drift nor removes
  # undeclared overrides. Fail before altering any existing topic in that case.
  validate_existing_topic "$name" "$partitions" "${configs[@]}"

  # Reconcile only the explicitly manifested configuration keys.
  "$kafka_configs" --bootstrap-server "$bootstrap_server" --alter \
    --entity-type topics --entity-name "$name" --add-config "$joined"
}

create_topic olist_cdc.olist_oltp.customers 1 cleanup.policy=delete retention.ms=604800000
create_topic olist_cdc.olist_oltp.orders 3 cleanup.policy=delete retention.ms=604800000
create_topic olist_cdc.olist_oltp.order_items 3 cleanup.policy=delete retention.ms=604800000
create_topic olist_cdc.olist_oltp.order_payments 3 cleanup.policy=delete retention.ms=604800000
create_topic olist_cdc.olist_oltp.order_reviews 3 cleanup.policy=delete retention.ms=604800000
create_topic olist_cdc.olist_oltp.products 1 cleanup.policy=delete retention.ms=604800000
create_topic olist_cdc.olist_oltp.sellers 1 cleanup.policy=delete retention.ms=604800000
create_topic olist_cdc.olist_oltp.product_category_translation 1 cleanup.policy=delete retention.ms=604800000
create_topic olist_cdc.transaction 1 cleanup.policy=delete retention.ms=604800000
create_topic olist_cdc.heartbeat 1 cleanup.policy=delete retention.ms=604800000
create_topic olist_cdc 1 cleanup.policy=delete retention.ms=-1 retention.bytes=-1
create_topic olist_cdc.schema_history 1 cleanup.policy=delete retention.ms=-1 retention.bytes=-1
create_topic olist_connect_configs 1 cleanup.policy=compact retention.ms=-1
create_topic olist_connect_offsets 25 cleanup.policy=compact retention.ms=-1
create_topic olist_connect_status 5 cleanup.policy=compact retention.ms=-1

echo "Kafka topic contract bootstrapped: 15 topics"
