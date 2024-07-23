import abc
import asyncio


class AbstractDebugServer(abc.ABC):
    """Abstract server class for DAP(Debug Adapter Protocol)"""

    @abc.abstractmethod
    async def startup(self, **kwargs) -> asyncio.subprocess.Process:
        raise NotImplementedError()

    @abc.abstractmethod
    async def shutdown(self, **kwargs) -> None:
        raise NotImplementedError()
