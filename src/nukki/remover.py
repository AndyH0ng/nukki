"""Thin wrapper around rembg's session/inference API.

Isolated from core.py's pure functions because importing this module pulls in
rembg and onnxruntime, and the underlying model call downloads weights on
first use (all in rembg, not here).
"""

from __future__ import annotations

import sys

from rembg import new_session, remove

from nukki.core import COREML_CACHE_DIR, ProviderList


class BackgroundRemover:
    def __init__(self, model: str, providers: ProviderList, verbose: bool = False) -> None:
        if any(isinstance(p, tuple) for p in providers):
            COREML_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._session = new_session(model, providers=providers)
        if verbose:
            active = self._session.inner_session.get_providers()
            print(f"[nukki] requested providers: {providers}", file=sys.stderr)
            print(f"[nukki] active providers:    {active}", file=sys.stderr)

    def remove(self, image_bytes: bytes) -> bytes:
        return remove(image_bytes, session=self._session)
