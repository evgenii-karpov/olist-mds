#!/bin/sh
set -eu

MANIFEST_FILE="${1:?manifest file required}"
DEST_DIR="${2:?destination directory required}"

mkdir -p "$DEST_DIR"

URL="https://repo1.maven.org/maven2/org/scala-sbt/sbt-launch/1.12.11/sbt-launch-1.12.11.jar"
TARGET_FILE="$DEST_DIR/sbt-launch.jar"

wget -q -O "$TARGET_FILE" "$URL"

EXPECTED_SHA=$(awk '{print $1}' "$MANIFEST_FILE")
ACTUAL_SHA=$(sha256sum "$TARGET_FILE" | awk '{print $1}')

if [ "$EXPECTED_SHA" != "$ACTUAL_SHA" ]; then
    echo "sbt-launch SHA-256 mismatch! Expected $EXPECTED_SHA, got $ACTUAL_SHA" >&2
    exit 1
fi
