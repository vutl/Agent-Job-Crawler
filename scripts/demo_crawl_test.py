import asyncio
import os
import sys
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from apps.crawler.monitors.foorilla import FOORILLA_TOPICS, is_paywall_or_login, FoorillaMonitor
from apps.crawler.normalizer import clean_html_to_text
from apps.analyzer.prefilter import is_prefilter_pass

def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

async def main():
    print_header("FULL 58 FOORILLA TOPICS & PAYWALL TRACKING SYSTEM")

    print("\n[Parsed Main Topics]:")
    main_topics = [
        "Data, AI, and Machine Learning",
        "Blockchain, Crypto & Web3",
        "Finance & Fintech",
        "InfoSec & Privacy",
        "Media, Simulation & Specialized Applications",
        "Software Engineering & Development",
        "Systems, Devices & Infrastructure"
    ]
    for topic in main_topics:
        slug = FOORILLA_TOPICS.get(topic, "")
        print(f"  • {topic:<45} -> slug: {slug}")

    print("\n[Sample Sub-Topics (Total 51 Sub-Topics)]:")
    sub_samples = [
        "Artificial Intelligence", "Machine Learning", "MLOps", "Data Engineering",
        "Data Science", "Natural Language Processing (NLP)", "Computer Vision",
        "Back-End Development", "Full-Stack Development", "DevOps", "Cybersecurity",
        "Quantitative and Algorithmic Trading", "Web3 Development", "Workflow Automation"
    ]
    for topic in sub_samples:
        slug = FOORILLA_TOPICS.get(topic, "")
        print(f"  • {topic:<45} -> slug: {slug}")

    # DEMO PAYWALL TRACKING AUDIT
    print_header("PAYWALL & LOGIN-WALL AUDIT LOG SYSTEM")

    paywall_url = "https://foorilla.com/account/login/?next=/hiring/jobs/3388387/apply/"
    paywall_html_sample = "<html><head><title>Sign In - foo🦍</title></head><body><h1>Sign in to your foo🦍 account</h1><p>Please choose a subscription plan to apply for premium job listings.</p></body></html>"

    is_paywall, paywall_reason = is_paywall_or_login(paywall_url, paywall_html_sample)

    print(f" -> Outbound Apply URL: {paywall_url}")
    print(f" -> Paywall Status Detected: {is_paywall}")
    print(f" -> Audit Reason Logged: {paywall_reason}")
    print(" -> Tracking Mechanism:")
    print("    • Saved to DB with status='active' and description_text='PAYWALL_DETECTED'")
    print("    • Pre-Filter flags is_relevant=False, relevance_reason='Paywall / Login wall detected'")
    print("    • 💰 0 Tokens Spent on LLM!")
    print("    • 📊 Trackable via API endpoint GET /api/v1/jobs?is_relevant=false")

if __name__ == "__main__":
    asyncio.run(main())
