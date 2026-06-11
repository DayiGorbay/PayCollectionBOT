from __future__ import annotations


class PanelError(Exception):
    """خطای پایه ارتباط با پنل."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class PanelAuthError(PanelError):
    pass


class PanelNotFoundError(PanelError):
    pass


class PanelConflictError(PanelError):
    pass


class PanelValidationError(PanelError):
    pass


class PanelTransportError(PanelError):
    pass
