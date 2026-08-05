#!/usr/bin/env sh
set -eu

properties_file=${SPARK_PROPERTIES_FILE:-/run/spark/conf/olist-lakehouse.properties}

python3 -m streaming.spark.platform.render_spark_properties --output "${properties_file}"

exec /opt/spark/bin/spark-submit --properties-file "${properties_file}" "$@"
