#!/usr/bin/env sh
set -eu

# The common image intentionally combines the local S3A/MinIO path with the
# GCP REST catalog and gs:// checkpoint path.  Keep the high-risk shared API
# classes single-owner so a future dependency update cannot silently change
# classpath precedence.

jar_files() {
    find /opt/spark/jars /opt/olist/jars -maxdepth 1 -type f -name '*.jar' -print
}

manifest_dir=$(mktemp -d)
trap 'rm -rf "${manifest_dir}"' EXIT INT TERM
manifest_files=''
manifest_index=0
while IFS= read -r jar_file; do
    manifest_file="${manifest_dir}/${manifest_index}.manifest"
    jar tf "${jar_file}" >"${manifest_file}"
    printf '%s\t%s\n' "${manifest_file}" "$(basename "${jar_file}")" >>"${manifest_dir}/owners"
    manifest_files="${manifest_files} ${manifest_file}"
    manifest_index=$((manifest_index + 1))
done <<EOF
$(jar_files)
EOF

assert_single_owner() {
    class_name=$1
    owners=$(grep -l -F -x -- "${class_name}" ${manifest_files} 2>/dev/null || true)
    count=$(printf '%s\n' "${owners}" | sed '/^$/d' | wc -l | tr -d ' ')
    owner_names=''
    for owner in ${owners}; do
        owner_names="${owner_names} $(sed -n "s#^${owner}\t##p" "${manifest_dir}/owners")"
    done
    test "${count}" -eq 1 || {
        echo "classpath conflict for ${class_name}: expected one owner, found ${count}:${owner_names}" >&2
        exit 1
    }
}

for class_name in \
    com/google/auth/oauth2/GoogleCredentials.class \
    com/google/cloud/hadoop/fs/gcs/GoogleHadoopFileSystem.class \
    com/google/protobuf/Message.class \
    com/google/common/collect/ImmutableList.class \
    com/fasterxml/jackson/databind/ObjectMapper.class \
    org/apache/http/client/HttpClient.class \
    org/apache/hadoop/fs/FileSystem.class \
    org/apache/iceberg/gcp/gcs/GCSFileIO.class; do
    assert_single_owner "${class_name}"
done
