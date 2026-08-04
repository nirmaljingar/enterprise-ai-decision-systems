"""Content-addressed identity for the policy snapshot a decision was judged under.

The determinism contract keys on the policy snapshot, and the audit use case is to prove which
policy a past decision was judged against. Neither works if the snapshot is an anonymous dict, so
it is hashed into a short stable id that travels on the audit record.
"""

import hashlib
import json
from typing import Any

DIGEST_LENGTH = 16


def policy_snapshot_id(snapshot: dict[str, Any]) -> str:
    """Return a stable ``pol_<digest>`` identity for a policy snapshot.

    The digest is taken over the canonical JSON form (sorted keys), so two snapshots that differ
    only in key order share an id, and any change to a limit produces a different one.
    """
    canonical = json.dumps(snapshot, sort_keys=True, separators=(",", ":"), default=str)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:DIGEST_LENGTH]
    return f"pol_{digest}"


__all__ = ["DIGEST_LENGTH", "policy_snapshot_id"]
