"""
Inventory hashing utility.

Computes a deterministic SHA-256 digest over a canonical JSON representation
of an inventory payload.  The hash is used by the backend to detect duplicate
submissions and skip unchanged snapshots without writing to the database.
"""

import hashlib
import json


def compute_inventory_hash(payload: dict) -> str:
    """
    Compute a stable SHA-256 hex digest for an inventory payload dictionary.

    The hash is deterministic: given the same logical data the output is always
    identical regardless of key insertion order, Python version, or platform.

    Parameters
    ----------
    payload:
        A plain-Python dictionary produced by a serialization helper.
        All values must already be JSON-serializable primitive types
        (``str``, ``int``, ``float``, ``bool``, ``None``, nested ``dict``/
        ``list`` of the same).  **Do not** pass raw Pydantic models or
        ``datetime`` objects — serialize them first.

    Returns
    -------
    str
        64-character lowercase hexadecimal SHA-256 digest.

    Notes
    -----
    * ``sort_keys=True`` ensures field insertion order never influences the
      digest.
    * ``separators=(",", ":")`` removes all optional whitespace so the
      canonical form is as compact and unambiguous as possible.
    * UTF-8 encoding is used throughout; the backend uses the same encoding
      when verifying the hash on arrival.
    """
    canonical: str = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
