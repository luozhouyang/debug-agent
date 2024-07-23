import asyncio
import logging
import os
import subprocess

from .abc_dap import AbstractDebugServer

logger = logging.getLogger(__name__)


class DebugpyDebugServer(AbstractDebugServer):
    """Debugpy debug server implementation.
    For more details, see: https://github.com/microsoft/debugpy

    """

    def __init__(self, venv_path: str = None, **kwargs):
        self._venv_path = venv_path
        if not self._venv_path:
            logger.info("No venv_path provided, creating a new one")
            self._create_venv(**kwargs)
        self._venv_python_path = os.path.join(self._venv_path, "bin", "python")
        self._debug_process = None

    def _create_venv(self, **kwargs):
        venv_dir = os.path.abspath(".venv")
        # makedirs and create venv
        if not os.path.exists(venv_dir):
            os.makedirs(venv_dir)
        venv_path = os.path.join(venv_dir, "dap-server-debugpy")
        cmd = ["python3", "-m", "venv", venv_path]
        # run cmd in subprocess module
        proc = subprocess.run(cmd, check=True)
        # check proc status
        if proc.returncode != 0:
            logger.error(f"venv creation failed: {proc.stderr}")
            raise RuntimeError(f"venv creation failed: {proc.stderr}")
        # log info if success
        logger.info(f"venv created successfully, venv_path: {venv_path}")

        # install depdendencies using venv path and pip
        cmd = [os.path.join(venv_path, "bin", "pip"), "install", "debugpy"]
        proc = subprocess.run(cmd, check=True)
        if proc.returncode != 0:
            logger.error(f"pip install failed: {proc.stderr}")
            raise RuntimeError(f"pip install failed: {proc.stderr}")
        logger.info("pip install debugpy success")
        self._venv_path = venv_path

    async def startup(
        self, filename: str = None, host: str = "127.0.0.1", port: int = 4432, **kwargs
    ) -> asyncio.subprocess.Process:
        """Startup debugpy debug server"""
        if self._debug_process:
            logger.warning("debugpy debug server already started")
            return self._debug_process

        cmd = [self._venv_python_path, "-m", "debugpy", "--listen", f"{host}:{port}", "--wait-for-client", "--log-to-stderr"]
        if filename:
            cmd.append(filename)
        cmd_line = " ".join(cmd)
        # run cmd in asyncio subprocess module
        proc = await asyncio.create_subprocess_shell(
            cmd_line,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        logger.info(f"Starting debugpy debug server: {cmd_line}")
        self._debug_process = proc
        # log process id
        logger.info(f"debugpy debug server pid: {proc.pid}")

        return self._debug_process

    async def shutdown(self, **kwargs) -> None:
        """Shutdown debugpy debug server"""
        if not self._debug_process:
            logger.warning("debugpy debug server not started")
            return
        self._debug_process.kill()
        await self._debug_process.wait()
