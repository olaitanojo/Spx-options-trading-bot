"""
Health check endpoints for SPX Options Trading Bot
Provides Kubernetes readiness, liveness, and startup probes
"""

import asyncio
import time
from datetime import datetime
from typing import Any, Dict

import psycopg2
import redis
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from psycopg2 import sql


class HealthChecker:
    """Health check service for monitoring application status"""

    def __init__(self):
        self.start_time = time.time()
        self.ready = False
        self.redis_client = None
        self.db_connection = None

    async def startup_check(self) -> Dict[str, Any]:
        """Startup probe - checks if application is starting up"""
        uptime = time.time() - self.start_time

        return {
            "status": "starting" if uptime < 30 else "ready",
            "uptime_seconds": uptime,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "application": "starting" if uptime < 10 else "ready",
                "dependencies": "checking" if uptime < 30 else "ready",
            },
        }

    async def readiness_check(self) -> Dict[str, Any]:
        """Readiness probe - checks if application is ready to serve traffic"""
        checks = {}
        overall_status = "ready"

        # Check Redis connectivity
        try:
            if self.redis_client is None:
                self.redis_client = redis.Redis.from_url(
                    "redis://spx-redis-service:6379"
                )

            self.redis_client.ping()
            checks["redis"] = {"status": "healthy", "response_time_ms": 0}
        except Exception as e:
            checks["redis"] = {"status": "unhealthy", "error": str(e)}
            overall_status = "not_ready"

        # Check Database connectivity
        try:
            if self.db_connection is None or self.db_connection.closed:
                self.db_connection = psycopg2.connect(
                    "postgresql://trading_user:password@spx-postgres-service:5432/trading_db"
                )

            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

            checks["database"] = {"status": "healthy", "response_time_ms": 0}
        except Exception as e:
            checks["database"] = {"status": "unhealthy", "error": str(e)}
            overall_status = "not_ready"

        # Check application readiness
        checks["application"] = {
            "status": "ready" if self.ready else "not_ready",
            "uptime_seconds": time.time() - self.start_time,
        }

        if not self.ready:
            overall_status = "not_ready"

        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks,
        }

    async def liveness_check(self) -> Dict[str, Any]:
        """Liveness probe - checks if application is alive"""
        uptime = time.time() - self.start_time

        # Simple liveness check - if we can respond, we're alive
        return {
            "status": "alive",
            "uptime_seconds": uptime,
            "timestamp": datetime.utcnow().isoformat(),
            "process_id": "trading-bot-main",
        }

    def set_ready(self, ready: bool):
        """Set application ready status"""
        self.ready = ready


# Global health checker instance
health_checker = HealthChecker()

# FastAPI app for health endpoints
health_app = FastAPI(title="SPX Options Trading Bot Health", version="1.0.0")


@health_app.get("/health")
async def health():
    """General health endpoint"""
    return await health_checker.liveness_check()


@health_app.get("/health/live")
async def liveness():
    """Kubernetes liveness probe endpoint"""
    try:
        result = await health_checker.liveness_check()
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse(
            content={"status": "unhealthy", "error": str(e)}, status_code=500
        )


@health_app.get("/health/ready")
async def readiness():
    """Kubernetes readiness probe endpoint"""
    try:
        result = await health_checker.readiness_check()

        if result["status"] == "ready":
            return JSONResponse(content=result, status_code=200)
        else:
            return JSONResponse(content=result, status_code=503)

    except Exception as e:
        return JSONResponse(
            content={"status": "not_ready", "error": str(e)}, status_code=503
        )


@health_app.get("/health/startup")
async def startup():
    """Kubernetes startup probe endpoint"""
    try:
        result = await health_checker.startup_check()
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse(
            content={"status": "starting", "error": str(e)}, status_code=200
        )


@health_app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    uptime = time.time() - health_checker.start_time

    # Simple metrics in Prometheus format
    metrics_data = f"""# HELP spx_bot_uptime_seconds Application uptime in seconds
# TYPE spx_bot_uptime_seconds counter
spx_bot_uptime_seconds {uptime}

# HELP spx_bot_ready Application readiness status
# TYPE spx_bot_ready gauge
spx_bot_ready {1 if health_checker.ready else 0}

# HELP spx_bot_info Application information
# TYPE spx_bot_info gauge
spx_bot_info{{version="1.0.0",environment="production"}} 1
"""

    return JSONResponse(content=metrics_data, media_type="text/plain", status_code=200)


if __name__ == "__main__":
    import uvicorn

    # Set ready after a startup delay
    async def delayed_ready():
        await asyncio.sleep(10)  # Simulate startup time
        health_checker.set_ready(True)

    # Start the task
    asyncio.create_task(delayed_ready())

    # Run the health check server
    uvicorn.run(health_app, host="0.0.0.0", port=8000)
