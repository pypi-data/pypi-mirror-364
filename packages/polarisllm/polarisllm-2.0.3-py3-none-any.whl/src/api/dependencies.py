"""
FastAPI Dependencies for PolarisLLM API
"""

from typing import Optional

from fastapi import HTTPException

from src.core.runtime import PolarisRuntime

# Global runtime instance (set by server.py)
_runtime: Optional[PolarisRuntime] = None

def set_runtime(runtime: PolarisRuntime) -> None:
    """Set the global runtime instance"""
    global _runtime
    _runtime = runtime

def get_runtime() -> PolarisRuntime:
    """Get the global runtime instance for FastAPI dependency injection"""
    if _runtime is None:
        raise HTTPException(status_code=503, detail="Runtime not initialized")
    return _runtime 