"""LMS provider implementations and the provider boundary used by workers."""

from ..config import AppConfig
from .base import LMSProvider
from .np_brightspace import BrightspaceProvider, NPBrightspaceProvider


def create_provider(config: AppConfig) -> LMSProvider:
    if config.provider_id == "np_brightspace":
        return NPBrightspaceProvider(config)
    if config.provider_id == "custom_brightspace":
        return BrightspaceProvider(config)
    raise ValueError(f"Unknown LMS provider: {config.provider_id}")


__all__ = [
    "BrightspaceProvider",
    "LMSProvider",
    "NPBrightspaceProvider",
    "create_provider",
]
