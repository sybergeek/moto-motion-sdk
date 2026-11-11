"""Explicit preview approval and full-render enforcement."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .models import ApprovalStatus


def compute_revision_id(value: Mapping[str, Any] | str) -> str:
    payload = value if isinstance(value, str) else json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class ApprovalRecord:
    reel_id: str
    revision_id: str
    preview_manifest_id: str | None
    status: ApprovalStatus
    approved_by: str | None = None
    note: str | None = None
    bypass_reason: str | None = None
    updated_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["status"] = self.status.value
        return value


@dataclass(frozen=True)
class FullRenderGate:
    allowed: bool
    reason: str
    approval_status: ApprovalStatus
    bypassed: bool = False


class ApprovalStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self) -> ApprovalRecord | None:
        if not self.path.exists():
            return None
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return ApprovalRecord(**{**data, "status": ApprovalStatus(data["status"])})

    def save(self, record: ApprovalRecord) -> ApprovalRecord:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(record.to_dict(), indent=2) + "\n", encoding="utf-8")
        return record

    def mark_preview_ready(self, *, reel_id: str, revision_id: str, preview_manifest_id: str, note: str | None = None) -> ApprovalRecord:
        return self.save(ApprovalRecord(reel_id, revision_id, preview_manifest_id, ApprovalStatus.PREVIEW_READY, note=note, updated_at=datetime.now(timezone.utc).isoformat()))

    def request_changes(self, *, reel_id: str, revision_id: str, preview_manifest_id: str | None, note: str) -> ApprovalRecord:
        return self.save(ApprovalRecord(reel_id, revision_id, preview_manifest_id, ApprovalStatus.CHANGES_REQUESTED, note=note, updated_at=datetime.now(timezone.utc).isoformat()))

    def approve(self, *, reel_id: str, revision_id: str, preview_manifest_id: str, approved_by: str, note: str | None = None) -> ApprovalRecord:
        if not approved_by.strip():
            raise ValueError("approved_by is required")
        return self.save(ApprovalRecord(reel_id, revision_id, preview_manifest_id, ApprovalStatus.APPROVED, approved_by=approved_by, note=note, updated_at=datetime.now(timezone.utc).isoformat()))

    def check_full_render(self, *, reel_id: str, revision_id: str, preview_manifest_id: str | None, bypass_reason: str | None = None) -> FullRenderGate:
        record = self.load()
        if bypass_reason:
            return FullRenderGate(True, f"Explicit bypass: {bypass_reason}", record.status if record else ApprovalStatus.NOT_REVIEWED, True)
        if record is None:
            return FullRenderGate(False, "No CQG approval record exists.", ApprovalStatus.NOT_REVIEWED)
        if record.reel_id != reel_id or record.revision_id != revision_id or record.preview_manifest_id != preview_manifest_id:
            return FullRenderGate(False, "CQG approval does not match the requested creative revision or preview.", record.status)
        if record.status is not ApprovalStatus.APPROVED:
            return FullRenderGate(False, f"CQG status is {record.status.value}; APPROVED is required.", record.status)
        return FullRenderGate(True, "Matching CQG approval found.", record.status)

