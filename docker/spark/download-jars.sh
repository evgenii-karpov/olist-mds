#!/usr/bin/env sh
set -eu

manifest=${1:?usage: download-jars.sh MANIFEST DESTINATION}
destination=${2:?usage: download-jars.sh MANIFEST DESTINATION}

mkdir -p "${destination}"

while read -r expected_sha256 url filename; do
    case "${expected_sha256}" in
        ''|'#'*) continue ;;
    esac

    case "${url}" in
        https://repo.maven.apache.org/maven2/*) ;;
        *)
            echo "refusing non-Maven-Central artifact URL for ${filename}" >&2
            exit 1
            ;;
    esac

    case "${filename}" in
        */*|'')
            echo "invalid destination filename: ${filename}" >&2
            exit 1
            ;;
    esac

    target="${destination}/${filename}"
    wget --https-only --quiet --output-document="${target}.part" "${url}"
    # GNU's equivalent spelling is sha256sum --check --strict; Alpine BusyBox
    # provides the portable -c form used here.
    printf '%s  %s\n' "${expected_sha256}" "${target}.part" | sha256sum -c
    mv "${target}.part" "${target}"
done < "${manifest}"

test "$(find "${destination}" -type f -name '*.jar' | wc -l | tr -d ' ')" -eq 12
