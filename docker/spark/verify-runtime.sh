#!/usr/bin/env sh
set -eu

expected_spark_version=${SPARK_VERSION:?SPARK_VERSION is required}
expected_scala_binary_version=${SCALA_BINARY_VERSION:?SCALA_BINARY_VERSION is required}
expected_hadoop_version=${HADOOP_VERSION:?HADOOP_VERSION is required}

spark_version=$(/opt/spark/bin/spark-submit --version 2>&1 | sed -n 's/.*version \([0-9][0-9.]*\).*/\1/p' | head -n 1)
test "${spark_version}" = "${expected_spark_version}" || {
    echo "Spark base image mismatch: expected ${expected_spark_version}, found ${spark_version:-unknown}" >&2
    exit 1
}

scala_library=$(find /opt/spark/jars -maxdepth 1 -type f -name 'scala-library-*.jar' | head -n 1)
test -n "${scala_library}" || {
    echo "Spark base image does not contain scala-library" >&2
    exit 1
}
case "$(basename "${scala_library}")" in
    scala-library-${expected_scala_binary_version}.*.jar) ;;
    *)
        echo "Scala base image mismatch: expected ${expected_scala_binary_version}.x, found $(basename "${scala_library}")" >&2
        exit 1
        ;;
esac

for component in api runtime; do
    matches=$(find /opt/spark/jars -maxdepth 1 -type f -name "hadoop-client-${component}-*.jar")
    count=$(printf '%s\n' "${matches}" | sed '/^$/d' | wc -l | tr -d ' ')
    test "${count}" -eq 1 || {
        echo "expected exactly one hadoop-client-${component} jar, found ${count}" >&2
        exit 1
    }
    case "$(basename "${matches}")" in
        hadoop-client-${component}-${expected_hadoop_version}.jar) ;;
        *)
            echo "Hadoop base image mismatch: expected ${expected_hadoop_version}, found $(basename "${matches}")" >&2
            exit 1
            ;;
    esac
done

test -f "/opt/spark/jars/hadoop-aws-${expected_hadoop_version}.jar"

for required in \
    "iceberg-spark-runtime-4.1_2.13-1.11.0.jar" \
    "iceberg-aws-bundle-1.11.0.jar" \
    "iceberg-gcp-bundle-1.11.0.jar" \
    "gcs-connector-hadoop3-2.2.31-shaded.jar" \
    "spark-sql-kafka-0-10_2.13-${expected_spark_version}.jar" \
    "spark-avro_2.13-${expected_spark_version}.jar" \
    "mysql-connector-j-9.7.0.jar"; do
    test -f "/opt/spark/jars/${required}" || {
        echo "required runtime artifact is missing: ${required}" >&2
        exit 1
    }
done

test -f "/opt/olist/jars/olist-spark-jobs.jar" || {
    echo "Application JAR /opt/olist/jars/olist-spark-jobs.jar is missing" >&2
    exit 1
}

if jar tf /opt/olist/jars/olist-spark-jobs.jar | grep -qE '^org/apache/(spark|iceberg|kafka|avro)/'; then
    echo "Application JAR contains provided dependencies!" >&2
    exit 1
fi
