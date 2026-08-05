#!/usr/bin/env sh
set -eu

source_dir=${CREDENTIAL_SOURCE_DIR:-/run/polaris-credentials}
target_dir=${CREDENTIAL_PROJECTION_DIR:-/run/projected-credentials}
contract_file=${CREDENTIAL_PROJECTION_CONTRACT:-/opt/olist/polaris/projection-contract.json}
consumer=${CREDENTIAL_CONSUMER:?CREDENTIAL_CONSUMER is required}
target_uid=${CREDENTIAL_TARGET_UID:?CREDENTIAL_TARGET_UID is required}
target_gid=${CREDENTIAL_TARGET_GID:?CREDENTIAL_TARGET_GID is required}

fail() {
    echo "$*" >&2
    exit 1
}

case ${target_uid} in
    '' | *[!0-9]*) fail "CREDENTIAL_TARGET_UID must be numeric" ;;
esac
case ${target_gid} in
    '' | *[!0-9]*) fail "CREDENTIAL_TARGET_GID must be numeric" ;;
esac

test "$(id -u)" = 0 || fail "credential projector must run as root"
test "${source_dir}" != "${target_dir}" ||
    fail "credential source and projection directories must be different"
test -d "${source_dir}" && test ! -L "${source_dir}" ||
    fail "credential source must be a real directory"
if test -e "${target_dir}" || test -L "${target_dir}"; then
    test -d "${target_dir}" && test ! -L "${target_dir}" ||
        fail "credential projection target must be a real directory"
fi
test -r "${contract_file}" || fail "credential projection contract is missing"

jq -e --arg consumer "${consumer}" \
    '.consumers[$consumer] != null' "${contract_file}" >/dev/null ||
    fail "unknown credential consumer ${consumer}"
jq -e --arg consumer "${consumer}" '
    .contract_version == 1
    and .security_model == "one-dedicated-volume-per-consumer"
    and (.consumers[$consumer].files | type) == "array"
    and (.consumers[$consumer].files | length) > 0
    and all(
        .consumers[$consumer].files[];
        (.source | type) == "string"
        and (.source | test("^[A-Za-z0-9][A-Za-z0-9._-]*$"))
        and (.environment | type) == "string"
        and (.environment | test("^[A-Z][A-Z0-9_]*_FILE$"))
    )
    and (
        [.consumers[$consumer].files[].source] | length
    ) == (
        [.consumers[$consumer].files[].source] | unique | length
    )
' "${contract_file}" >/dev/null ||
    fail "invalid credential projection contract for ${consumer}"

expected_files=$(jq -r --arg consumer "${consumer}" \
    '.consumers[$consumer].files[].source' "${contract_file}")

is_expected_file() {
    candidate=$1
    for expected_file in ${expected_files}; do
        if test "${candidate}" = "${expected_file}"; then
            return 0
        fi
    done
    return 1
}

cleanup_projection_temps() {
    for expected_file in ${expected_files}; do
        rm -f "${target_dir}/.${expected_file}.tmp"
    done
}

trap cleanup_projection_temps EXIT
trap 'exit 1' HUP INT TERM

umask 077
mkdir -p "${target_dir}"
test -d "${target_dir}" && test ! -L "${target_dir}" ||
    fail "credential projection target must be a real directory"
cleanup_projection_temps
chown "${target_uid}:${target_gid}" "${target_dir}"
chmod 0700 "${target_dir}"

for existing_path in \
    "${target_dir}"/* \
    "${target_dir}"/.[!.]* \
    "${target_dir}"/..?*; do
    if test ! -e "${existing_path}" && test ! -L "${existing_path}"; then
        continue
    fi
    existing_name=${existing_path##*/}
    if ! is_expected_file "${existing_name}"; then
        fail "unexpected artifact in dedicated ${consumer} projection: ${existing_name}"
    fi
    test -f "${existing_path}" && test ! -L "${existing_path}" ||
        fail "existing projected artifact must be a regular file: ${existing_name}"
done

for expected_file in ${expected_files}; do
    source_path="${source_dir}/${expected_file}"
    target_path="${target_dir}/${expected_file}"
    temp_path="${target_dir}/.${expected_file}.tmp"

    test -f "${source_path}" && test ! -L "${source_path}" ||
        fail "missing regular credential artifact ${source_path}"
    test -s "${source_path}" || fail "empty credential artifact ${source_path}"
    test "$(stat -c '%a' "${source_path}")" = 600 ||
        fail "credential source must have mode 0600: ${source_path}"
    test "$(stat -c '%u:%g' "${source_path}")" = 0:0 ||
        fail "credential source must be owned by root: ${source_path}"

    cp "${source_path}" "${temp_path}"
    chown "${target_uid}:${target_gid}" "${temp_path}"
    chmod 0600 "${temp_path}"
    mv "${temp_path}" "${target_path}"
done

for expected_file in ${expected_files}; do
    target_path="${target_dir}/${expected_file}"
    test -f "${target_path}" && test ! -L "${target_path}" ||
        fail "projected credential is not a regular file: ${target_path}"
    test "$(stat -c '%a' "${target_path}")" = 600 ||
        fail "projected credential must have mode 0600: ${target_path}"
    test "$(stat -c '%u:%g' "${target_path}")" = \
        "${target_uid}:${target_gid}" ||
        fail "projected credential has the wrong owner: ${target_path}"
done

printf '%s\n' "credential projection for ${consumer} is ready"
