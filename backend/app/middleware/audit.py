import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time

logger = logging.getLogger("healthcare_platform.audit")


class AuditLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs every mutating API call (POST/PUT/PATCH/DELETE)
    to the audit_logs table asynchronously.
    """

    SKIP_PATHS = {"/api/v1/health", "/docs", "/openapi.json", "/redoc"}
    LOG_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response: Response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000, 2)

        if (
            request.method in self.LOG_METHODS
            and request.url.path not in self.SKIP_PATHS
            and request.url.path.startswith("/api/")
        ):
            # Fire-and-forget audit write (non-blocking)
            try:
                await self._write_audit(request, response.status_code, duration_ms)
            except Exception as exc:
                logger.warning(f"Audit log write failed: {exc}")

        return response

    async def _write_audit(self, request: Request, status_code: int, duration_ms: float):
        from app.core.database import SessionLocal
        from app.models.all_models import AuditLog
        from app.core.security import decode_token

        user_id = None
        token = request.headers.get("Authorization", "")
        if token.startswith("Bearer "):
            try:
                payload = decode_token(token.split(" ")[1])
                user_id = int(payload.get("sub", 0)) if payload else None
            except Exception:
                pass

        path_parts = request.url.path.strip("/").split("/")
        resource = path_parts[2] if len(path_parts) >= 3 else request.url.path
        resource_id = path_parts[3] if len(path_parts) >= 4 else None

        ip = request.client.host if request.client else "unknown"

        db = SessionLocal()
        try:
            log = AuditLog(
                user_id=user_id,
                action=request.method,
                resource=resource,
                resource_id=resource_id,
                details_json={
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                    "query_params": str(request.query_params)
                },
                ip_address=ip
            )
            db.add(log)
            db.commit()
        finally:
            db.close()
