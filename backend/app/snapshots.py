"""Doorstep snapshot storage: local directory by default, S3 when a bucket is set.

Refs are opaque strings stored on the event row: `local://<path>` or
`s3://<bucket>/<key>`. The API layer turns refs into file responses or
presigned URLs without knowing which backend produced them.
"""

import logging
from datetime import UTC, datetime
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from .config import Settings

logger = logging.getLogger(__name__)

CONTENT_TYPE = "image/jpeg"


class SnapshotStore:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._dir = Path(settings.snapshots_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._s3 = boto3.client("s3", region_name=settings.aws_region) if settings.s3_bucket else None

    @property
    def mode(self) -> str:
        return "s3" if self._s3 else "local"

    def save(self, event_id: str, image: bytes) -> str:
        day = datetime.now(UTC).strftime("%Y%m%d")
        key = f"snapshots/{day}/{event_id}.jpg"
        if self._s3:
            bucket = self._settings.s3_bucket
            self._s3.put_object(Bucket=bucket, Key=key, Body=image, ContentType=CONTENT_TYPE)
            return f"s3://{bucket}/{key}"
        path = self._dir / day / f"{event_id}.jpg"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(image)
        return f"local://{path}"

    def resolve(self, ref: str) -> tuple[bytes | None, str | None]:
        """Return (image_bytes, redirect_url) — exactly one side is populated."""
        if ref.startswith("s3://") and self._s3:
            bucket, _, key = ref.removeprefix("s3://").partition("/")
            try:
                url = self._s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket, "Key": key},
                    ExpiresIn=self._settings.snapshot_presign_seconds,
                )
                return None, url
            except ClientError as exc:
                logger.warning("Presign failed for %s: %s", ref, exc)
                return None, None
        if ref.startswith("local://"):
            path = self.local_path(ref)
            if path and path.exists():
                return path.read_bytes(), None
        return None, None

    def local_path(self, ref: str) -> Path | None:
        """Path for a local:// ref, None for other schemes or escapes."""
        if not ref.startswith("local://"):
            return None
        path = Path(ref.removeprefix("local://")).resolve()
        return path if self._dir.resolve() in path.parents or path.parent == self._dir.resolve() else None
