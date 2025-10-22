from __future__ import annotations

import asyncio
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from playwright.async_api import BrowserContext, Playwright, async_playwright


class PlaywrightController:
    """Manage a persistent Playwright WebKit context across GUI actions."""

    def __init__(self, profile_dir: Path) -> None:
        self.profile_dir = profile_dir
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._playwright: Optional[Playwright] = None
        self._context: Optional[BrowserContext] = None
        self._lock = threading.Lock()

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _ensure_playwright(self) -> Playwright:
        if self._playwright is None:
            self._playwright = await async_playwright().start()
        return self._playwright

    async def _ensure_context(self, headless: bool = False) -> BrowserContext:
        await self._ensure_playwright()
        if self._context is None:
            self.profile_dir.mkdir(parents=True, exist_ok=True)
            self._context = await self._playwright.webkit.launch_persistent_context(
                str(self.profile_dir),
                headless=headless,
            )
        return self._context

    def open_login(self, url: str) -> asyncio.Future:
        """Launch (or reuse) the persistent browser in headful mode."""

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
        future = asyncio.run_coroutine_threadsafe(self._close_browser(), self._loop)
        future.result()

    async def _close_browser(self) -> None:
        async with self._context_lock():
            if self._context is not None:
                await self._context.close()
                self._context = None

    def validate_session(self, probe_url: Optional[str] = None) -> bool:
        future = asyncio.run_coroutine_threadsafe(self._validate_session(probe_url), self._loop)
        return future.result()

    async def _validate_session(self, probe_url: Optional[str]) -> bool:
        async with self._context_lock():
            if self._context is not None:
                # Close headful context if still open to avoid conflicts.
                await self._context.close()
                self._context = None

            playwright = await self._ensure_playwright()
            # Launch a temporary headless context to inspect storage state.
            context = await playwright.webkit.launch_persistent_context(
                str(self.profile_dir),
                headless=True,
            )
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
        future = asyncio.run_coroutine_threadsafe(self._shutdown(), self._loop)
        future.result()
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join()

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

