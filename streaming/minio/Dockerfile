FROM golang:1.24.8-bookworm AS build

ARG MINIO_VERSION=RELEASE.2025-10-15T17-29-55Z
ENV CGO_ENABLED=0

RUN go install github.com/minio/minio@${MINIO_VERSION}

FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 minio \
    && useradd --uid 1000 --gid minio --home-dir /home/minio --create-home minio \
    && mkdir -p /data \
    && chown minio:minio /data

COPY --from=build /go/bin/minio /usr/local/bin/minio
COPY start.sh /usr/local/bin/start-minio

RUN chmod +x /usr/local/bin/start-minio

USER minio
EXPOSE 9000 9001
ENTRYPOINT ["/usr/local/bin/start-minio"]
CMD ["server", "/data", "--console-address", ":9001"]

