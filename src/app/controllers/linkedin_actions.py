"""High-level automation tasks for LinkedIn navigation and scraping."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from playwright.async_api import Error as PlaywrightError, Page, TimeoutError as PlaywrightTimeoutError

from .browser import LinkedInBrowserController
from ..models.scrap_user import ExperienceRecord, ScrapUserRepository


class LinkedInActionsController:
    """Encapsulate LinkedIn navigation flows after the login is complete."""

    JOBS_URL = "https://www.linkedin.com/jobs/?"
    PROFILE_URL_PATTERN = re.compile(r"/in/[^/]+/?")

    def __init__(
        self,
        browser: LinkedInBrowserController,
        scrap_repository: ScrapUserRepository,
    ) -> None:
        self._browser = browser
        self._scrap_repository = scrap_repository

    # -- public API ---------------------------------------------------------
    def open_jobs_page(self):
        """Open the LinkedIn jobs section, trying a direct URL first."""

        return self._browser.run_with_page(self._open_jobs_page)

    def open_profile_page(self):
        """Navigate to the logged user's profile page."""

        return self._browser.run_with_page(self._open_profile_page)

    def capture_profile_snapshot(self):
        """Open the profile page, scrape relevant data and persist it locally."""

        return self.scan_profile()

    def scan_profile(self):
        """Run the profile scraping routine ensuring duplicate-free storage."""

        return self._browser.run_with_page(self._capture_profile_snapshot)

    # -- core automation routines ------------------------------------------
    async def _open_jobs_page(self, page: Page) -> str:
        await page.wait_for_load_state("domcontentloaded")
        if await self._try_open_jobs_via_url(page):
            return page.url
        await self._click_jobs_navigation(page)
        await self._ensure_jobs_url(page)
        return page.url

    async def _open_profile_page(self, page: Page) -> str:
        await page.wait_for_load_state("domcontentloaded")
        if self.PROFILE_URL_PATTERN.search(page.url):
            return page.url
        await self._click_profile_entry(page)
        await self._ensure_profile_url(page)
        return page.url

    async def _capture_profile_snapshot(self, page: Page) -> Dict[str, List[Any]]:
        await self._open_profile_page(page)
        name = await self._extract_profile_name(page)
        experiences = await self._extract_experiences(page)
        education = await self._extract_section_items(page, "education")
        licenses = await self._extract_section_items(page, "licenses_and_certifications")
        projects = await self._extract_section_items(page, "projects")
        skills = await self._extract_section_items(page, "skills")
        recommendations = await self._extract_section_items(page, "recommendations")
        publications = await self._extract_section_items(page, "publications")
        payload = self._scrap_repository.update(
            nome=name,
            experiencias=[record.to_dict() for record in experiences],
            formacao=education,
            licencas=licenses,
            projetos=projects,
            competencias=skills,
            recomendacoes=recommendations,
            publicacoes=publications,
        )
        return payload

    # -- helpers ------------------------------------------------------------
    async def _try_open_jobs_via_url(self, page: Page) -> bool:
        try:
            await page.goto(self.JOBS_URL, wait_until="domcontentloaded")
        except PlaywrightError:
            return False
        return "linkedin.com/jobs" in page.url

    async def _click_jobs_navigation(self, page: Page) -> None:
        selectors = [
            "a[href='https://www.linkedin.com/jobs/?']",
            "a.global-nav__primary-link[href*='/jobs/']",
            "a[data-test-app-aware-link][href*='/jobs/']",
            "a:has(span:has-text('Vagas'))",
        ]
        for selector in selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=4000)
            except PlaywrightTimeoutError:
                continue
            if element is None:
                continue
            await element.click()
            return
        raise RuntimeError("Não foi possível localizar o link de vagas do LinkedIn.")

    async def _ensure_jobs_url(self, page: Page) -> None:
        try:
            await page.wait_for_url("**/jobs/**", timeout=20000)
        except PlaywrightTimeoutError:
            if "/jobs" not in page.url:
                raise RuntimeError("Não foi possível abrir a página de vagas do LinkedIn.")

    async def _click_profile_entry(self, page: Page) -> None:
        selectors = [
            "div.profile-card a.profile-card-profile-link",
            "div.profile-card a.profile-card-profile-picture-container",
            "div.profile-card-member-details a[href^='/in/']",
            "a[href^='/in/']:has(img[alt*='Ver perfil'])",
        ]
        for selector in selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=4000)
            except PlaywrightTimeoutError:
                continue
            if element is None:
                continue
            href = await element.get_attribute("href")
            await element.click()
            if href and href.startswith("/in/"):
                await page.wait_for_load_state("networkidle")
            return
        raise RuntimeError("Não foi possível localizar o link do perfil do usuário.")

    async def _ensure_profile_url(self, page: Page) -> None:
        try:
            await page.wait_for_url("**/in/**", timeout=20000)
        except PlaywrightTimeoutError:
            if not self.PROFILE_URL_PATTERN.search(page.url):
                raise RuntimeError("A página do perfil do usuário não pôde ser aberta.")

    async def _extract_profile_name(self, page: Page) -> str:
        selectors = ["main h1", "h1"]
        for selector in selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=4000)
            except PlaywrightTimeoutError:
                continue
            if element is None:
                continue
            text = (await element.inner_text()).strip()
            if text:
                return text
        return ""

    async def _extract_experiences(self, page: Page) -> List[ExperienceRecord]:
        try:
            section = await page.wait_for_selector("section:has(#experience)", timeout=4000)
        except PlaywrightTimeoutError:
            return []
        records: List[ExperienceRecord] = []
        entries = section.locator("div[data-view-name='profile-component-entity']")
        count = await entries.count()
        for index in range(count):
            entry = entries.nth(index)
            record = await self._parse_experience_entry(entry)
            if record is not None:
                records.append(record)
        return records

    async def _parse_experience_entry(self, entry) -> Optional[ExperienceRecord]:
        details_selector = "a[href*='add-edit/POSITION']"
        try:
            details = entry.locator(details_selector)
            if await details.count() == 0:
                details = entry.locator("a[href*='/details/experience']")
            if await details.count() == 0:
                return None
            text = await details.first.inner_text()
        except PlaywrightTimeoutError:
            return None

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cargo = lines[0] if lines else ""
        empresa = lines[1] if len(lines) > 1 else ""
        periodo = lines[2] if len(lines) > 2 else ""
        local = lines[3] if len(lines) > 3 else ""

        descricao = ""
        description_locator = entry.locator("div[class*='inline-show-more-text']")
        if await description_locator.count() > 0:
            raw_description = await description_locator.first.inner_text()
            descricao = raw_description.replace("…ver mais", "").replace("ver mais", "").strip()

        record = ExperienceRecord(
            cargo=cargo,
            empresa=empresa,
            periodo=periodo,
            local=local,
            descricao=descricao,
        )
        if not any(record.to_dict().values()):
            return None
        return record

    async def _extract_section_items(self, page: Page, anchor_id: str) -> List[str]:
        selectors = [
            f"section:has(#{anchor_id})",
            f"section[id='{anchor_id}']",
            f"section[data-section='{anchor_id}']",
        ]
        for selector in selectors:
            try:
                section = await page.wait_for_selector(selector, timeout=3000)
            except PlaywrightTimeoutError:
                continue
            if section is None:
                continue
            entries = section.locator("li.artdeco-list__item, li.pvs-list__item")
            count = await entries.count()
            results: List[str] = []
            for index in range(count):
                text = await entries.nth(index).inner_text()
                cleaned_lines = [line.strip() for line in text.splitlines() if line.strip()]
                cleaned = " \u2013 ".join(cleaned_lines)
                if cleaned:
                    results.append(cleaned)
            if results:
                return results
        return []


__all__ = ["LinkedInActionsController"]
