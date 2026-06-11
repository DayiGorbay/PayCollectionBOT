from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

import httpx

from app.core.errors import PanelAuthError, PanelConflictError, PanelError, PanelNotFoundError, PanelTransportError

logger = logging.getLogger(__name__)

RETRYABLE_STATUS = frozenset({429, 502, 503, 504})
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 3


class PanelHttpClient:
    """HTTP client with retry, timeout, and structured logging for panel APIs."""

    def __init__(
        self,
        *,
        panel_id: int,
        panel_type: str,
        timeout: float = DEFAULT_TIMEOUT,
        verify_ssl: bool = False,
    ) -> None:
        self.panel_id = panel_id
        self.panel_type = panel_type
        self.timeout = timeout
        self.verify_ssl = verify_ssl

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: Any = None,
        data: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        retries: int = MAX_RETRIES,
    ) -> httpx.Response:
        last_exc: Exception | None = None
        for attempt in range(retries):
            started = time.monotonic()
            try:
                async with httpx.AsyncClient(timeout=self.timeout, verify=self.verify_ssl) as client:
                    response = await client.request(
                        method,
                        url,
                        headers=headers,
                        json=json,
                        data=data,
                        params=params,
                    )
            except httpx.HTTPError as exc:
                last_exc = exc
                duration_ms = int((time.monotonic() - started) * 1000)
                logger.warning(
                    "panel_transport_error panel_id=%s type=%s method=%s url=%s attempt=%s duration_ms=%s error=%s",
                    self.panel_id,
                    self.panel_type,
                    method,
                    url,
                    attempt + 1,
                    duration_ms,
                    exc,
                )
                if attempt < retries - 1:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                raise PanelTransportError(str(exc)) from exc

            duration_ms = int((time.monotonic() - started) * 1000)
            logger.info(
                "panel_request panel_id=%s type=%s method=%s url=%s status=%s duration_ms=%s",
                self.panel_id,
                self.panel_type,
                method,
                url,
                response.status_code,
                duration_ms,
            )

            if response.status_code in RETRYABLE_STATUS and attempt < retries - 1:
                await asyncio.sleep(0.5 * (attempt + 1))
                continue

            return response

        raise PanelTransportError(str(last_exc or "request failed"))

    def raise_for_status(self, response: httpx.Response, *, context: str = "") -> None:
        if response.status_code < 400:
            return
        detail = self._extract_error_detail(response)
        msg = f"{context}: {detail}".strip(": ") if context else detail
        code = response.status_code
        if code == 401:
            raise PanelAuthError(msg, status_code=code)
        if code == 404:
            raise PanelNotFoundError(msg, status_code=code)
        if code == 409:
            raise PanelConflictError(msg, status_code=code)
        if code == 422:
            from app.core.errors import PanelValidationError

            raise PanelValidationError(msg, status_code=code)
        raise PanelError(msg, status_code=code)

    @staticmethod
    def _extract_error_detail(response: httpx.Response) -> str:
        try:
            body = response.json()
            if isinstance(body, dict):
                return str(body.get("detail") or body.get("msg") or body)
        except Exception:
            pass
        text = (response.text or "").strip()
        return text[:500] if text else f"HTTP {response.status_code}"
