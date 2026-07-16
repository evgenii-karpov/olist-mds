from __future__ import annotations

import hashlib
import json
from pathlib import Path

from botocore.exceptions import ClientError
from nifiapi.flowfiletransform import FlowFileTransform, FlowFileTransformResult
from nifiapi.properties import PropertyDescriptor, StandardValidators


class PutImmutableS3Object(FlowFileTransform):
    class Java:
        implements = ["org.apache.nifi.python.processor.FlowFileTransform"]

    class ProcessorDetails:
        version = "1.0.0"
        description = (
            "Write an immutable S3-compatible object and publish its manifest last."
        )
        tags = ["olist", "cdc", "s3", "minio", "manifest"]

    def __init__(self, **kwargs):
        super().__init__()
        self.endpoint = PropertyDescriptor(
            name="Endpoint URL",
            description="S3-compatible endpoint.",
            required=True,
            default_value="http://minio:9000",
            validators=[StandardValidators.NON_EMPTY_VALIDATOR],
        )
        self.region = PropertyDescriptor(
            name="Region",
            description="S3 signing region.",
            required=True,
            default_value="us-east-1",
        )
        self.bucket = PropertyDescriptor(
            name="Bucket",
            description="Destination bucket.",
            required=True,
            default_value="olist-cdc",
        )
        self.access_key = PropertyDescriptor(
            name="Access Key",
            description="Service account access key.",
            required=True,
            default_value="olist_nifi",
        )
        self.secret_file = PropertyDescriptor(
            name="Secret Key File",
            description="Docker secret containing the service password.",
            required=True,
            default_value="/run/secrets/minio_nifi_password",
        )
        self.write_manifest = PropertyDescriptor(
            name="Write Manifest",
            description="Publish a closed-object manifest after data.",
            required=True,
            default_value="true",
            allowable_values=["true", "false"],
        )

    def getPropertyDescriptors(self):
        return [
            self.endpoint,
            self.region,
            self.bucket,
            self.access_key,
            self.secret_file,
            self.write_manifest,
        ]

    def onScheduled(self, context):
        import boto3

        secret = (
            Path(context.getProperty(self.secret_file).getValue())
            .read_text(encoding="utf-8")
            .strip()
        )
        self.bucket_name = context.getProperty(self.bucket).getValue()
        self.manifests = context.getProperty(self.write_manifest).getValue() == "true"
        self.client = boto3.client(
            "s3",
            endpoint_url=context.getProperty(self.endpoint).getValue(),
            region_name=context.getProperty(self.region).getValue(),
            aws_access_key_id=context.getProperty(self.access_key).getValue(),
            aws_secret_access_key=secret,
        )

    def _head(self, key: str):
        try:
            return self.client.head_object(Bucket=self.bucket_name, Key=key)
        except ClientError as exc:
            code = str(exc.response.get("Error", {}).get("Code", ""))
            if code in {"404", "NoSuchKey", "NotFound"}:
                return None
            raise

    def _put_once(self, key: str, body: bytes, content_type: str) -> tuple[str, bool]:
        digest = hashlib.sha256(body).hexdigest()
        existing = self._head(key)
        if existing is not None:
            if existing.get("Metadata", {}).get("sha256") != digest:
                raise ValueError(f"immutable object conflict for {key}")
            return str(existing.get("ETag", "")).strip('"'), True
        response = self.client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=body,
            ContentType=content_type,
            Metadata={"sha256": digest, "contract-version": "1"},
        )
        return str(response.get("ETag", "")).strip('"'), False

    def transform(self, context, flowfile):
        attributes = flowfile.getAttributes()
        key = attributes.get("cdc.object.key")
        if not key:
            return FlowFileTransformResult(
                relationship="failure",
                attributes={"cdc.error.reason": "cdc.object.key is missing"},
            )
        body = bytes(flowfile.getContentsAsBytes())
        try:
            etag, duplicate = self._put_once(
                key, body, attributes.get("mime.type", "application/octet-stream")
            )
            digest = hashlib.sha256(body).hexdigest()
            manifest_key = attributes.get("cdc.manifest.key")
            if self.manifests and manifest_key:
                manifest = {
                    "contract_version": 1,
                    "flow_version": "olist-cdc-v1",
                    "kind": attributes.get("cdc.kind"),
                    "table": attributes.get("cdc.table"),
                    "topic": attributes.get("cdc.topic"),
                    "partition": int(attributes.get("cdc.partition", "-1")),
                    "schema_id": attributes.get("cdc.schema_id"),
                    "covered_offset_ranges": json.loads(
                        attributes.get("cdc.covered_offset_ranges", "[]")
                    ),
                    "row_count": int(attributes.get("cdc.row_count", "0")),
                    "operation_counts": json.loads(
                        attributes.get("cdc.operation_counts", "{}")
                    ),
                    "source_ts_min": attributes.get("cdc.source_ts_min") or None,
                    "source_ts_max": attributes.get("cdc.source_ts_max") or None,
                    "closed_at": attributes.get("cdc.closed_at"),
                    "object": {
                        "uri": f"s3://{self.bucket_name}/{key}",
                        "etag": etag,
                        "sha256": digest,
                        "size_bytes": len(body),
                    },
                }
                manifest_body = json.dumps(
                    manifest, sort_keys=True, separators=(",", ":")
                ).encode()
                self._put_once(manifest_key, manifest_body, "application/json")
            return FlowFileTransformResult(
                relationship="success",
                attributes={
                    "s3.bucket": self.bucket_name,
                    "s3.key": key,
                    "s3.etag": etag,
                    "cdc.object.sha256": digest,
                    "cdc.object.duplicate": str(duplicate).lower(),
                },
            )
        except ValueError as exc:
            return FlowFileTransformResult(
                relationship="failure", attributes={"cdc.error.reason": str(exc)[:512]}
            )
