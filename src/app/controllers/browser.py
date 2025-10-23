"""Low-level Playwright controller shared across the application."""
from __future__ import annotations

import asyncio
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Awaitable, Callable, Optional, TypeVar

from playwright.async_api import (
    BrowserContext,
    Error as PlaywrightError,
    Playwright,
    TimeoutError as PlaywrightTimeoutError,
    Page,
    async_playwright,
)


T = TypeVar("T")


class LinkedInBrowserController:
    """Manage a persistent Playwright WebKit context across GUI actions."""

    HOME_URL = "https://www.linkedin.com/"
    LOGIN_URL = "https://www.linkedin.com/login/pt"

    def __init__(self, profile_dir: Path) -> None:
        self.profile_dir = profile_dir
        self._loop = asyncio.new_event_loop()
        self._loop_ready = threading.Event()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._playwright: Optional[Playwright] = None
        self._context: Optional[BrowserContext] = None
        self._lock = threading.Lock()
        self._ensure_webkit_installed()

    # -- event loop bootstrap -----------------------------------------------
    def _ensure_webkit_installed(self) -> None:
        import os
        import subprocess
        import sys

        try:
            from playwright._impl._driver import get_driver_dir

            driver_dir = get_driver_dir()
            webkit_path = os.path.join(driver_dir, "webkit")
            if not os.path.exists(webkit_path):
                subprocess.run([sys.executable, "-m", "playwright", "install", "webkit"], check=True)
        except Exception:
            subprocess.run([sys.executable, "-m", "playwright", "install", "webkit"], check=True)

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop_ready.set()
        self._loop.run_forever()

    # -- helpers ------------------------------------------------------------
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

    def _ensure_loop_ready(self) -> bool:
        self._loop_ready.wait()
        return not (self._loop.is_closed() or not self._loop.is_running())

    # -- public API ---------------------------------------------------------
    def open_page(self, url: str) -> asyncio.Future:
        """Launch (or reuse) the persistent browser in headful mode."""

        if not self._ensure_loop_ready():
            raise RuntimeError("O controlador do Playwright já foi finalizado.")
        return asyncio.run_coroutine_threadsafe(self._open_page(url), self._loop)

    async def _open_page(self, url: str) -> None:
        async with self._context_lock():
            context = await self._ensure_context(headless=False)
            page = context.pages[0] if context.pages else await context.new_page()
            await page.goto(url, wait_until="domcontentloaded")

    def run_with_page(self, handler: Callable[[Page], Awaitable[T]]) -> asyncio.Future[T]:
        """Execute a coroutine with exclusive access to the current page."""

        if not self._ensure_loop_ready():
            raise RuntimeError("O controlador do Playwright já foi finalizado.")
        return asyncio.run_coroutine_threadsafe(self._run_with_page(handler), self._loop)

    async def _run_with_page(self, handler: Callable[[Page], Awaitable[T]]) -> T:
        async with self._context_lock():
            context = await self._ensure_context(headless=False)
            page = context.pages[0] if context.pages else await context.new_page()
            return await handler(page)

    def login_with_credentials(self, email: str, password: str) -> asyncio.Future:
        """Execute the LinkedIn login flow considering the dynamic homepage layout."""

        if not self._ensure_loop_ready():
            raise RuntimeError("O controlador do Playwright já foi finalizado.")
        return asyncio.run_coroutine_threadsafe(
            self._login_with_credentials(email, password),
            self._loop,
        )

    async def _login_with_credentials(self, email: str, password: str) -> str:
        async with self._context_lock():
            context = await self._ensure_context(headless=False)
            page = context.pages[0] if context.pages else await context.new_page()
            await page.goto(self.HOME_URL, wait_until="domcontentloaded")

            await self._click_first_available(
                page,
                [
                    "a.sign-in-form__sign-in-cta",
                    "a.remember-me-sign-in-cta",
                    "a.nav__button-secondary",
                ],
            )

            await self._click_if_exists(page, "button.signin-other-account")

            await page.wait_for_selector("input[name='session_key']", state="visible")
            await page.fill("input[name='session_key']", email)

            await page.wait_for_selector("input[name='session_password']", state="visible")
            await page.fill("input[name='session_password']", password)

            await page.click("button[data-litms-control-urn='login-submit']")

            try:
                await page.wait_for_url("**/feed/**", timeout=20000)
            except PlaywrightTimeoutError:
                await page.wait_for_load_state("networkidle")
            return page.url

    def close_browser(self) -> None:
        if not self._ensure_loop_ready():
            return
        future = asyncio.run_coroutine_threadsafe(self._close_browser(), self._loop)
        future.result()

    async def _close_browser(self) -> None:
        async with self._context_lock():
            if self._context is not None:
                await self._context.close()
                self._context = None

    def validate_session(self, probe_url: Optional[str] = None) -> bool:
        if not self._ensure_loop_ready():
            return False
        future = asyncio.run_coroutine_threadsafe(self._validate_session(probe_url), self._loop)
        return future.result()

    async def _validate_session(self, probe_url: Optional[str]) -> bool:
        async with self._context_lock():
            if self._context is not None:
                await self._context.close()
                self._context = None

            playwright = await self._ensure_playwright()
            try:
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
                        pass
                storage = await context.storage_state()
                return bool(storage.get("cookies") or storage.get("origins"))
            finally:
                await context.close()

    def shutdown(self) -> None:
        self._loop_ready.wait()
        if self._loop.is_closed():
            return
        if not self._loop.is_running():
            return
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

    # -- helpers ------------------------------------------------------------
    @asynccontextmanager
    async def _context_lock(self):
        with self._lock:
            yield

    async def _click_if_exists(self, page, selector: str, timeout: int = 2000) -> None:
        try:
            element = await page.wait_for_selector(selector, timeout=timeout)
        except PlaywrightTimeoutError:
            return
        if element:
            await element.click()

    async def _click_first_available(self, page, selectors: list[str]) -> None:
        for selector in selectors:
            element = await page.query_selector(selector)
            if element:
                await element.click()
                return
        await page.goto(self.LOGIN_URL, wait_until="domcontentloaded")


__all__ = ["LinkedInBrowserController"]
