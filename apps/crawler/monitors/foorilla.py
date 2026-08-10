import re
import httpx
import logging
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Any, Tuple
from apps.crawler.monitors.base import BaseATSMonitor
from apps.crawler.normalizer import clean_html_to_text, compute_content_hash, normalize_canonical_url
from packages.schemas import NormalizedJobPost

logger = logging.getLogger(__name__)

# Complete Foorilla Main and Sub Topics mapping (58 topics)
FOORILLA_TOPICS = {
    # Main topics
    "Data, AI, and Machine Learning": "data-ai-and-machine-learning",
    "Blockchain, Crypto & Web3": "blockchain-crypto-and-web3",
    "Finance & Fintech": "finance-and-fintech",
    "InfoSec & Privacy": "infosec-and-privacy",
    "Media, Simulation & Specialized Applications": "media-simulation-and-specialized-applications",
    "Software Engineering & Development": "software-engineering-and-development",
    "Systems, Devices & Infrastructure": "systems-devices-and-infrastructure",

    # Sub topics
    "3D Modeling and Simulation": "3d-modeling-and-simulation",
    "Artificial Intelligence": "artificial-intelligence",
    "AR/VR": "ar-vr",
    "Audio Signal Processing": "audio-signal-processing",
    "Autonomous Systems": "autonomous-systems",
    "Back-End Development": "back-end-development",
    "Big Data": "big-data",
    "Bioinformatics": "bioinformatics",
    "Blockchain": "blockchain",
    "Browser Extension Development": "browser-extension-development",
    "Cloud Computing": "cloud-computing",
    "Computer Vision": "computer-vision",
    "Cryptographic Software": "cryptographic-software",
    "Cybersecurity": "cybersecurity",
    "Databases": "databases",
    "Data Engineering": "data-engineering",
    "Data Science": "data-science",
    "Decentralized Finance (DeFi)": "decentralized-finance-defi",
    "DevOps": "devops",
    "DevSecOps": "devsecops",
    "Digital Forensics": "digital-forensics",
    "Edge Computing": "edge-computing",
    "Embedded Systems": "embedded-systems",
    "Enterprise Software": "enterprise-software",
    "Financial Platforms and Digital Banking": "financial-platforms-and-digital-banking",
    "Firmware Development": "firmware-development",
    "Front-End Development": "front-end-development",
    "Full-Stack Development": "full-stack-development",
    "Game Development": "game-development",
    "GIS Software": "gis-software",
    "IoT (Internet of Things)": "iot-internet-of-things",
    "Localization and Internationalization": "localization-and-internationalization",
    "Low-Code/No-Code Platforms": "low-code-no-code-platforms",
    "Machine Learning": "machine-learning",
    "Mainframe Programming": "mainframe-programming",
    "Microservices": "microservices",
    "MLOps": "mlops",
    "Mobile App Development": "mobile-app-development",
    "Natural Language Processing (NLP)": "natural-language-processing-nlp",
    "Operating Systems": "operating-systems",
    "Payment Systems": "payment-systems",
    "Penetration Testing": "penetration-testing",
    "Quantitative and Algorithmic Trading": "quantitative-and-algorithmic-trading",
    "Quantum Computing": "quantum-computing",
    "Reverse Engineering": "reverse-engineering",
    "Robotic Process Automation (RPA)": "robotic-process-automation-rpa",
    "Robotics Control Software": "robotics-control-software",
    "SCADA Systems": "scada-systems",
    "Scientific Computing": "scientific-computing",
    "Scripting and Automation": "scripting-and-automation",
    "Testing and QA": "testing-and-qa",
    "Video Processing": "video-processing",
    "Wearable Device Software": "wearable-device-software",
    "Web3 Development": "web3-development",
    "WebAssembly (Wasm)": "webassembly-wasm",
    "Web Development": "web-development",
    "Workflow Automation": "workflow-automation",
}

# Paywall and Login Wall patterns
PAYWALL_URL_PATTERNS = [
    r"/account/login", r"/login", r"/signin", r"/auth", r"/pricing", r"/checkout", r"/subscribe", r"/paywall"
]
PAYWALL_HTML_PATTERNS = [
    r"sign in to continue", r"choose a plan", r"subscribe to access", r"create an account to apply", r"paywall"
]

def is_paywall_or_login(url: str, html_text: str = "") -> Tuple[bool, str]:
    """Checks if a destination URL or HTML response is a paywall / login wall."""
    url_lower = url.lower()
    for pattern in PAYWALL_URL_PATTERNS:
        if re.search(pattern, url_lower):
            return True, f"Destination URL matches paywall/login pattern '{pattern}'"

    if html_text:
        html_lower = html_text.lower()
        for pattern in PAYWALL_HTML_PATTERNS:
            if re.search(pattern, html_lower):
                return True, f"Page content matches paywall/login indicator '{pattern}'"

    return False, ""

class FoorillaMonitor(BaseATSMonitor):
    """Monitor for Foorilla Job Aggregator (https://foorilla.com/)."""

    @property
    def ats_name(self) -> str:
        return "foorilla"

    def parse_job_items_from_html(self, html_content: str, filter_junior_only: bool = False, filter_remote_only: bool = False) -> List[Dict[str, Any]]:
        """
        Parses Foorilla job list items from HTML (e.g. format4.txt).
        Extracts title, level_tag ([EN], [SE], [MI]), remote_tag ([R], [WH], [WRA]), salary, location, and detail_path.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        items = soup.find_all("li", class_="list-group-item")

        parsed_jobs = []
        for item in items:
            title_a = item.find("a", class_="stretched-link")
            if not title_a:
                continue

            title = title_a.get_text(strip=True)
            hx_get = title_a.get("hx-get", "")
            href = title_a.get("href", "")
            detail_path = hx_get or href

            level_tag_el = item.find("small", class_="text-warning-emphasis")
            level_code = level_tag_el.get_text(strip=True) if level_tag_el else ""

            remote_span = item.find("span", class_="text-success")
            remote_code = remote_span.get_text(strip=True) if remote_span else ""

            salary_span = item.find("small", class_=re.compile(r"text-bg-"))
            salary = salary_span.get_text(strip=True) if salary_span else ""

            loc_container = item.find("div", class_="text-end")
            location = loc_container.get_text(strip=True) if loc_container else "Remote"

            is_junior = "[EN]" in level_code or "junior" in title.lower() or "intern" in title.lower() or "co-op" in title.lower() or "trainee" in title.lower() or "entry" in title.lower()
            is_remote = "[R]" in remote_code or "[WRA]" in remote_code or "remote" in location.lower() or "remote" in title.lower()

            if filter_junior_only and not is_junior:
                continue
            if filter_remote_only and not is_remote:
                continue

            parsed_jobs.append({
                "title": title,
                "detail_path": detail_path,
                "level_code": level_code,
                "remote_code": remote_code,
                "is_junior": is_junior,
                "is_remote": is_remote,
                "salary": salary,
                "location": location,
            })

        return parsed_jobs

    async def fetch_jobs(
        self,
        company_name: str = "Foorilla Aggregated",
        board_token: str = "data-ai-and-machine-learning",
        junior_only: bool = True,
        remote_only: bool = True,
        track_paywalled_jobs: bool = True
    ) -> List[NormalizedJobPost]:
        """
        Fetches jobs from Foorilla for a given topic.
        If track_paywalled_jobs is True, paywalled jobs are returned with paywall flag for tracking (0 LLM tokens).
        """
        base_url = "https://foorilla.com"
        topic_slug = FOORILLA_TOPICS.get(board_token, board_token)
        list_url = f"{base_url}/hiring/jobs/?topic={topic_slug}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "HX-Request": "true",
        }

        normalized_posts: List[NormalizedJobPost] = []

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                res = await client.get(list_url, headers=headers)
                if res.status_code != 200:
                    logger.warning(f"Foorilla list endpoint returned status {res.status_code}")
                    return []

                parsed_items = self.parse_job_items_from_html(
                    res.text,
                    filter_junior_only=junior_only,
                    filter_remote_only=remote_only
                )

                seen_paths = set()
                for item_meta in parsed_items[:15]:
                    detail_path = item_meta["detail_path"]
                    if not detail_path or detail_path in seen_paths:
                        continue
                    seen_paths.add(detail_path)

                    detail_url = f"{base_url}{detail_path}" if detail_path.startswith("/") else detail_path

                    detail_res = await client.get(detail_url, headers=headers)
                    if detail_res.status_code != 200:
                        continue

                    # Check Paywall / Login wall on detail page
                    is_paywall, paywall_reason = is_paywall_or_login(str(detail_res.url), detail_res.text)
                    if is_paywall:
                        logger.info(f"Paywall detected for Foorilla job '{item_meta['title']}': {paywall_reason}")
                        if track_paywalled_jobs:
                            paywall_text = f"PAYWALL_DETECTED: {paywall_reason}"
                            normalized_posts.append(
                                NormalizedJobPost(
                                    external_id=detail_path.rstrip("/").split("-")[-1],
                                    canonical_url=normalize_canonical_url(str(detail_res.url)),
                                    company_name=company_name,
                                    company_domain="foorilla.com",
                                    title=item_meta["title"],
                                    location=item_meta["location"],
                                    description_raw=f"<p>{paywall_text}</p>",
                                    description_text=paywall_text,
                                    content_hash=compute_content_hash(paywall_text),
                                )
                            )
                        continue

                    detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                    h1 = detail_soup.find("h1")
                    title = h1.get_text(strip=True) if h1 else item_meta["title"]

                    apply_btn = detail_soup.find("a", class_=re.compile(r"btn-primary"))
                    apply_href = apply_btn.get("href", "") if apply_btn else ""

                    canonical_target_url = detail_url
                    if apply_href:
                        outbound_url = f"{base_url}{apply_href}" if apply_href.startswith("/") else apply_href
                        try:
                            head_res = await client.head(outbound_url, headers=headers)
                            target_url_str = str(head_res.url)

                            # Check Paywall / Login wall on outbound apply target
                            is_outbound_paywall, paywall_reason_out = is_paywall_or_login(target_url_str)
                            if is_outbound_paywall:
                                logger.info(f"Paywall detected on outbound apply link for '{title}': {paywall_reason_out}")
                                if track_paywalled_jobs:
                                    paywall_text = f"PAYWALL_DETECTED: {paywall_reason_out}"
                                    normalized_posts.append(
                                        NormalizedJobPost(
                                            external_id=detail_path.rstrip("/").split("-")[-1],
                                            canonical_url=normalize_canonical_url(target_url_str),
                                            company_name=company_name,
                                            company_domain="foorilla.com",
                                            title=title,
                                            location=item_meta["location"],
                                            description_raw=f"<p>{paywall_text}</p>",
                                            description_text=paywall_text,
                                            content_hash=compute_content_hash(paywall_text),
                                        )
                                    )
                                continue

                            canonical_target_url = target_url_str
                        except Exception:
                            canonical_target_url = outbound_url

                    desc_container = detail_soup.find("div", class_=re.compile(r"pb-2"))
                    raw_html = str(desc_container) if desc_container else detail_res.text
                    clean_text = clean_html_to_text(raw_html)

                    if not clean_text or len(clean_text) < 30:
                        continue

                    content_hash = compute_content_hash(clean_text)

                    normalized_posts.append(
                        NormalizedJobPost(
                            external_id=detail_path.rstrip("/").split("-")[-1],
                            canonical_url=normalize_canonical_url(canonical_target_url),
                            company_name=company_name,
                            company_domain="foorilla.com",
                            title=title,
                            location=item_meta["location"],
                            description_raw=raw_html,
                            description_text=clean_text,
                            content_hash=content_hash,
                        )
                    )
        except Exception as e:
            logger.error(f"Error fetching Foorilla jobs: {e}")

        return normalized_posts

    def parse_foorilla_html_snapshot(self, html_content: str, source_name: str = "Nokia") -> Optional[NormalizedJobPost]:
        """Parses a local HTML snapshot file of a Foorilla job card."""
        soup = BeautifulSoup(html_content, "html.parser")
        h1 = soup.find("h1")
        title = h1.get_text(strip=True) if h1 else "Unknown Job"

        apply_btn = soup.find("a", class_=re.compile(r"btn-primary"))
        apply_href = apply_btn.get("href", "") if apply_btn else "https://foorilla.com/hiring/jobs/apply"

        desc_container = soup.find("div", class_=re.compile(r"pb-2"))
        raw_html = str(desc_container) if desc_container else html_content
        clean_text = clean_html_to_text(raw_html)
        content_hash = compute_content_hash(clean_text)

        return NormalizedJobPost(
            external_id="3380156",
            canonical_url=normalize_canonical_url(apply_href),
            company_name=source_name,
            company_domain="foorilla.com",
            title=title,
            location="United States",
            description_raw=raw_html,
            description_text=clean_text,
            content_hash=content_hash,
        )
