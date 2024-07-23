import abc
import asyncio


class AbstractLanguageServer(abc.ABC):
    """Abstract server class for LSP(Language Server Protocol)"""

    @abc.abstractmethod
    async def startup(self, **kwargs) -> asyncio.subprocess.Process:
        raise NotImplementedError()

    @abc.abstractmethod
    async def shutdown(self, **kwargs) -> None:
        raise NotImplementedError()
