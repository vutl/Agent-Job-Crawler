import re
import html
import httpx
import logging
import urllib.parse
from bs4 import BeautifulSoup
from typing import Optional, Tuple
from apps.crawler.normalizer import clean_html_to_text

logger = logging.getLogger(__name__)

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"',
    "Upgrade-Insecure-Requests": "1",
}

HTMX_HEADERS = {
    **BROWSER_HEADERS,
    "HX-Request": "true",
}

DEFAULT_HEADERS = BROWSER_HEADERS

class DOMExtractor:
    """
    Universal Smart DOM Extractor for arbitrary outbound employer career portals
    (Lever, Greenhouse, Workday, BambooHR, SmartRecruiters, University/Corporate Portals).
    Compresses 100KB-1MB raw HTML down to 1-4KB clean structured Markdown with 0 LLM token waste.
    """

    @staticmethod
    def extract_company_name_from_foorilla_link(link_element) -> str:
        """Extracts clean, un-truncated company name from a Foorilla company link element."""
        if not link_element:
            return "Partner"
        raw_text = link_element.get_text(strip=True).replace("@", "").strip()
        # If text is not truncated (e.g. Mozilla, Wikimedia Foundation, Nokia Bell Labs), return it
        if raw_text and not raw_text.endswith("...") and len(raw_text) > 3:
            return raw_text
        # If truncated (e.g. B..., N..., T...), extract name from href slug
        href = link_element.get("href", "")
        if href:
            slug = href.strip("/").split("/")[-1]
            if slug.lower() in ["companies", "company", "hiring", ""]:
                return "Direct Employer"
            # Strip trailing ID number (-3125, -999)
            clean_slug = re.sub(r"-\d+$", "", slug).replace("-", " ")
            if clean_slug:
                return clean_slug.title()
        return "Direct Employer"

    @staticmethod
    def extract_company_name(soup: BeautifulSoup, target_url: str, fallback: str = "Partner") -> str:
        """Extracts the real employer company name from meta tags, title, or domain."""
        # 1. Try og:site_name
        og_site = soup.find("meta", property="og:site_name")
        if og_site and og_site.get("content"):
            name = og_site.get("content").strip()
            if name and name.lower() not in ["foorilla", "lever", "greenhouse", "workday", "smartrecruiters", "job", "careers"]:
                return name

        # 2. Try title patterns: 'Job Title at Company' or 'Company - Job Title' or 'Company | Job Title'
        if soup.title and soup.title.string:
            t = soup.title.string.strip()
            if " at " in t:
                return t.split(" at ")[-1].split("-")[0].split("|")[0].strip()
            elif " - " in t:
                parts = t.split(" - ")
                if len(parts) >= 2:
                    return parts[0].strip() if len(parts[0]) < 30 else parts[-1].strip()
            elif " | " in t:
                parts = t.split(" | ")
                if len(parts) >= 2:
                    return parts[0].strip() if len(parts[0]) < 30 else parts[-1].strip()

        # 3. Try parsing domain name
        try:
            parsed = urllib.parse.urlparse(target_url)
            netloc = parsed.netloc.lower()
            if "lever.co" in netloc:
                parts = parsed.path.strip("/").split("/")
                if parts:
                    return parts[0].capitalize()
            elif "greenhouse.io" in netloc:
                parts = parsed.path.strip("/").split("/")
                if parts:
                    return parts[0].capitalize()
            elif "universiteit" in netloc or "leiden" in netloc:
                return "Leiden University"
            elif "bt.com" in netloc:
                return "BT Group"
            elif "vaillant" in netloc:
                return "Vaillant Group"
            elif "tryg" in netloc:
                return "Tryg"
            elif "bam.com" in netloc:
                return "BAM Careers"
            elif "op-careers.fi" in netloc:
                return "OP Financial Group"
            elif netloc:
                domain_parts = netloc.replace("careers.", "").replace("jobs.", "").replace("www.", "").split(".")
                if domain_parts and len(domain_parts[0]) > 2:
                    return domain_parts[0].capitalize()
        except Exception:
            pass

        return fallback

    @staticmethod
    def extract_clean_job_markdown(html_content: str, target_url: str = "") -> Tuple[str, str]:
        """
        Strips DOM noise and extracts structured Markdown Job Description and real Company Name.
        Returns (company_name, clean_markdown_jd).
        """
        if not html_content:
            return "Partner", ""

        soup = BeautifulSoup(html_content, "html.parser")

        # 1. Extract Company Name before removing head
        company_name = DOMExtractor.extract_company_name(soup, target_url)

        # 2. Strip Noise Tags
        noise_selectors = [
            "script", "style", "noscript", "svg", "iframe", "nav", "header", "footer", "form", "aside",
            ".cookie-banner", "#cookie-banner", ".cookie-consent", "#cookie-consent",
            ".header", ".footer", ".navigation", ".navbar"
        ]
        for tag in soup(noise_selectors):
            tag.decompose()

        # 3. Locate Main Job Content Container
        main_content = (
            soup.find("div", class_=re.compile(r"posting-description|job-description|job-detail|description|content-body|job-info", re.I)) or
            soup.find("div", id=re.compile(r"job-description|job-detail|content|job-info", re.I)) or
            soup.find("main") or
            soup.find("article") or
            soup.body
        )

        raw_segment = str(main_content) if main_content else html_content
        clean_markdown = clean_html_to_text(raw_segment)

        return company_name, clean_markdown

    @classmethod
    async def resolve_outbound_apply_url(
        cls,
        foorilla_detail_url: str,
        apply_relative_or_abs_href: str,
    ) -> Optional[Tuple[str, str, str]]:
        """
        Follows Foorilla apply redirect using an isolated browser session.
        Returns (final_canonical_url, real_company_name, clean_markdown_jd) or None.
        """
        try:
            async with httpx.AsyncClient(timeout=20.0, headers=BROWSER_HEADERS) as client:
                # Step 1: Establish session on detail page to receive csrftoken cookie
                await client.get(foorilla_detail_url)

                # Step 2: Click Apply with Referer and navigation headers (without HX-Request)
                apply_full_url = urllib.parse.urljoin(foorilla_detail_url, apply_relative_or_abs_href)
                apply_headers = dict(BROWSER_HEADERS)
                apply_headers["Referer"] = foorilla_detail_url
                apply_headers["Sec-Fetch-Dest"] = "document"
                apply_headers["Sec-Fetch-Mode"] = "navigate"
                apply_headers["Sec-Fetch-Site"] = "same-origin"
                apply_headers["Sec-Fetch-User"] = "?1"

                r2 = await client.get(apply_full_url, headers=apply_headers, follow_redirects=True)
                if r2.status_code == 200:
                    final_url = str(r2.url)
                    if "foorilla.com" not in final_url:
                        # Successfully reached real employer ATS!
                        company, clean_jd = cls.extract_clean_job_markdown(r2.text, final_url)
                        if len(clean_jd) > 100:
                            return final_url, company, clean_jd
        except Exception as e:
            logger.warning(f"Error resolving outbound apply redirect for {foorilla_detail_url}: {e}")

        return None
