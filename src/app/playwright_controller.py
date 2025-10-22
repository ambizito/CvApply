from __future__ import annotations

import asyncio
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from playwright.async_api import (
    BrowserContext,
    Error as PlaywrightError,
    Playwright,
    async_playwright,
)


class PlaywrightController:
    """Manage a persistent Playwright WebKit context across GUI actions."""

    def __init__(self, profile_dir: Path) -> None:
        self.profile_dir = profile_dir
        self._loop = asyncio.new_event_loop()
        self._loop_ready = threading.Event()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._playwright: Optional[Playwright] = None
        self._context: Optional[BrowserContext] = None
        self._lock = threading.Lock()
        # Instala automaticamente o WebKit se necessário
        self._ensure_webkit_installed()

    def _ensure_webkit_installed(self):
        import subprocess, sys
        try:
            # Tenta importar o runtime do WebKit
            from playwright._impl._driver import get_driver_dir
            import os
            driver_dir = get_driver_dir()
            webkit_path = os.path.join(driver_dir, 'webkit')
            if not os.path.exists(webkit_path):
                subprocess.run([sys.executable, '-m', 'playwright', 'install', 'webkit'], check=True)
        except Exception:
            # Se falhar, tenta instalar mesmo assim
            subprocess.run([sys.executable, '-m', 'playwright', 'install', 'webkit'], check=True)

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop_ready.set()
        self._loop.run_forever()

    async def _ensure_playwright(self) -> Playwright:
        if self._playwright is None:
            self._playwright = await async_playwright().start()
        return self._playwright

    async def _ensure_context(self, headless: bool = False) -> BrowserContext:
        await self._ensure_playwright()
        if self._context is None:
            self.profile_dir.mkdir(parents=True, exist_ok=True)
            try:
                self._context = await self._playwright.webkit.launch_persistent_context(
                    str(self.profile_dir),
                    headless=headless,
                )
            except PlaywrightError as exc:  # pragma: no cover - runtime guard
                message = (
                    "Falha ao iniciar o WebKit persistente. Verifique se o runtime foi instalado com \n"
                    "`playwright install webkit` e tente novamente."
                )
                raise RuntimeError(message) from exc
        return self._context

    def open_login(self, url: str) -> asyncio.Future:
        """Launch (or reuse) the persistent browser in headful mode."""

        self._loop_ready.wait()
        if self._loop.is_closed():
            raise RuntimeError("O controlador do Playwright já foi finalizado.")
        if not self._loop.is_running():
            raise RuntimeError("O controlador do Playwright já foi finalizado.")
        return asyncio.run_coroutine_threadsafe(self._open_login(url), self._loop)

    async def _open_login(self, url: str) -> None:
        async with self._context_lock():
            context = await self._ensure_context(headless=False)
            if context.pages:
                page = context.pages[0]
                await page.bring_to_front()
            else:
                page = await context.new_page()
            await page.goto(url)

    def close_browser(self) -> None:
        self._loop_ready.wait()
        if self._loop.is_closed() or not self._loop.is_running():
            return
        future = asyncio.run_coroutine_threadsafe(self._close_browser(), self._loop)
        future.result()

    async def _close_browser(self) -> None:
        async with self._context_lock():
            if self._context is not None:
                await self._context.close()
                self._context = None

    def validate_session(self, probe_url: Optional[str] = None) -> bool:
        self._loop_ready.wait()
        if self._loop.is_closed() or not self._loop.is_running():
            return False
        future = asyncio.run_coroutine_threadsafe(self._validate_session(probe_url), self._loop)
        return future.result()

    async def _validate_session(self, probe_url: Optional[str]) -> bool:
        async with self._context_lock():
            if self._context is not None:
                # Close headful context if still open to avoid conflicts.
                await self._context.close()
                self._context = None

            playwright = await self._ensure_playwright()
            try:
                # Launch a temporary headless context to inspect storage state.
                context = await playwright.webkit.launch_persistent_context(
                    str(self.profile_dir),
                    headless=True,
                )
            except PlaywrightError as exc:  # pragma: no cover - runtime guard
                message = (
                    "Não foi possível validar o perfil persistente porque o runtime do WebKit não está disponível. \n"
                    "Execute `playwright install webkit` e repita a operação."
                )
                raise RuntimeError(message) from exc
            try:
                page = context.pages[0] if context.pages else await context.new_page()
                if probe_url:
                    try:
                        await page.goto(probe_url)
                    except Exception:
                        # Swallow navigation errors—the aim is simply to ensure cookies load.
                        pass
                storage = await context.storage_state()
                return bool(storage.get("cookies") or storage.get("origins"))
            finally:
                await context.close()

    def shutdown(self) -> None:
        self._loop_ready.wait()
        if self._loop.is_closed():
            return
        if self._loop.is_running():
            future = asyncio.run_coroutine_threadsafe(self._shutdown(), self._loop)
            future.result()
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._thread.join()
        self._loop.close()

    async def _shutdown(self) -> None:
        async with self._context_lock():
            if self._context is not None:
                await self._context.close()
                self._context = None
            if self._playwright is not None:
                await self._playwright.stop()
                self._playwright = None

    @asynccontextmanager
    async def _context_lock(self):
        # Use a synchronous lock to protect concurrent async operations.
        with self._lock:
            yield

