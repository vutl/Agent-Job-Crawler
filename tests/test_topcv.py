import pytest
from apps.crawler.monitors.topcv import TopCVMonitor

def test_topcv_slugify():
    assert TopCVMonitor.slugify("AI Engineer") == "ai-engineer"
    assert TopCVMonitor.slugify("Hà Nội") == "ha-noi"
    assert TopCVMonitor.slugify("Machine Learning & Deep Learning") == "machine-learning-deep-learning"

def test_topcv_build_search_url():
    url = TopCVMonitor.build_search_url("AI Engineer", "Hà Nội")
    assert url == "https://www.topcv.vn/tim-viec-lam-ai-engineer-tai-ha-noi-kl1"

def test_topcv_parse_search_html():
    with open("tests/fixtures/topcv/search_sample.html", encoding="utf-8") as f:
        html = f.read()

    monitor = TopCVMonitor()
    cards = monitor.parse_search_jobs(html, query="AI Engineer", max_jobs=5)

    assert len(cards) > 0
    assert cards[0]["external_id"] != ""
    assert "https://www.topcv.vn/viec-lam/" in cards[0]["url"]
    assert cards[0]["title"] != ""
    assert cards[0]["company"] != ""

def test_topcv_parse_detail_html():
    with open("tests/fixtures/topcv/detail_sample.html", encoding="utf-8") as f:
        html = f.read()

    monitor = TopCVMonitor()
    meta, desc_raw, desc_text = monitor.parse_job_detail(html, fallback_title="Default Title", fallback_company="Default Company")

    assert "AI Team Leader" in meta["title"]
    assert "ACWORKS" in meta["company"]
    assert desc_raw != ""
    assert desc_text != ""
