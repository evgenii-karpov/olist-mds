#!/usr/bin/env sh
set -eu

properties_file=${SPARK_PROPERTIES_FILE:-/run/spark/conf/olist-lakehouse.properties}
config_mode=${SPARK_CONFIG_MODE:-streaming}

python3 -m streaming.spark.platform.render_spark_properties \
    --output "${properties_file}" \
    --mode "${config_mode}"

exec /opt/spark/bin/spark-submit --properties-file "${properties_file}" "$@"
