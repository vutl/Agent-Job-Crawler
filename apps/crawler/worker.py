import os
import sys
import logging
import asyncio
from typing import Dict, Any

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from arq.connections import RedisSettings
from packages.database import SessionLocal, Base, engine
from apps.crawler.monitors.greenhouse import GreenhouseMonitor
from apps.crawler.monitors.lever import LeverMonitor
from apps.crawler.monitors.workday import WorkdayMonitor
from apps.crawler.monitors.foorilla import FoorillaMonitor
from apps.crawler.monitors.jobright import JobrightMonitor
from apps.crawler.store import save_normalized_job
from apps.analyzer.provider import OpenAICompatibleProvider, MockLLMProvider
from apps.analyzer.extractor import extract_and_save_job

logger = logging.getLogger(__name__)

def get_llm_provider():
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("LLM_MODEL")
    if api_key and base_url:
        return OpenAICompatibleProvider(base_url=base_url, api_key=api_key, model=model)
    return MockLLMProvider()

async def startup(ctx: Dict[str, Any]):
    """ARQ Worker startup handler."""
    logger.info("Initializing ARQ Worker context & database tables...")
    Base.metadata.create_all(bind=engine)
    ctx["db"] = SessionLocal()
    ctx["llm_provider"] = get_llm_provider()

async def shutdown(ctx: Dict[str, Any]):
    """ARQ Worker shutdown handler."""
    logger.info("Closing ARQ Worker database connection...")
    db = ctx.get("db")
    if db:
        db.close()

async def process_jobs(db, posts, provider):
    saved_count = 0
    analyzed_count = 0
    for post in posts:
        job, is_new = save_normalized_job(db, post)
        if is_new:
            saved_count += 1
            analysis = await extract_and_save_job(db, job, provider)
            analyzed_count += 1
            logger.info(f"Analyzed job '{job.title}' -> Role: {analysis.role_family} (Relevant: {analysis.is_relevant})")
    return saved_count, analyzed_count

async def crawl_greenhouse_task(ctx: Dict[str, Any], company_name: str, board_token: str):
    logger.info(f"[ARQ Task] Crawling Greenhouse for {company_name} ({board_token})...")
    monitor = GreenhouseMonitor()
    posts = await monitor.fetch_jobs(company_name, board_token)
    saved, analyzed = await process_jobs(ctx["db"], posts, ctx["llm_provider"])
    return f"Greenhouse {company_name}: fetched {len(posts)}, saved {saved}, analyzed {analyzed}"

async def crawl_lever_task(ctx: Dict[str, Any], company_name: str, board_token: str):
    logger.info(f"[ARQ Task] Crawling Lever for {company_name} ({board_token})...")
    monitor = LeverMonitor()
    posts = await monitor.fetch_jobs(company_name, board_token)
    saved, analyzed = await process_jobs(ctx["db"], posts, ctx["llm_provider"])
    return f"Lever {company_name}: fetched {len(posts)}, saved {saved}, analyzed {analyzed}"

async def crawl_workday_task(ctx: Dict[str, Any], company_name: str, board_token: str):
    logger.info(f"[ARQ Task] Crawling Workday for {company_name} ({board_token})...")
    monitor = WorkdayMonitor()
    posts = await monitor.fetch_jobs(company_name, board_token)
    saved, analyzed = await process_jobs(ctx["db"], posts, ctx["llm_provider"])
    return f"Workday {company_name}: fetched {len(posts)}, saved {saved}, analyzed {analyzed}"

async def crawl_foorilla_task(ctx: Dict[str, Any], topic_slug: str = "data-ai-and-machine-learning"):
    logger.info(f"[ARQ Task] Crawling Foorilla topic '{topic_slug}'...")
    monitor = FoorillaMonitor()
    posts = await monitor.fetch_jobs(company_name="Foorilla Aggregated", board_token=topic_slug)
    saved, analyzed = await process_jobs(ctx["db"], posts, ctx["llm_provider"])
    return f"Foorilla topic '{topic_slug}': fetched {len(posts)}, saved {saved}, analyzed {analyzed}"

async def crawl_jobright_task(ctx: Dict[str, Any], board_token: str = "recommend"):
    logger.info(f"[ARQ Task] Crawling Jobright topic '{board_token}'...")
    monitor = JobrightMonitor()
    posts = await monitor.fetch_jobs(company_name="Jobright Aggregated", board_token=board_token)
    saved, analyzed = await process_jobs(ctx["db"], posts, ctx["llm_provider"])
    return f"Jobright topic '{board_token}': fetched {len(posts)}, saved {saved}, analyzed {analyzed}"

class WorkerSettings:
    """ARQ Worker Configuration."""
    functions = [
        crawl_greenhouse_task,
        crawl_lever_task,
        crawl_workday_task,
        crawl_foorilla_task,
        crawl_jobright_task,
    ]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
    )
    max_jobs = 10
    poll_delay = 0.5
