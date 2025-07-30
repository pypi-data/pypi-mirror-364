# scheduler engine
# core logic of the scheduler

import logging
import asyncio
from functools import wraps
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR

from scheduler.jobs import PLATFORM_FACTORY
from scheduler.job_config import JOB_CONFIGS

from crawlers.discord_crawler import DiscordCrawler

# handling retries for jobs
def with_retries(fn, max_retries=3) -> callable:
    @wraps(fn)
    def wrapper(*args, **kwargs) -> callable:
        for attempt in range(max_retries):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                logging.warning(f"[Retry {attempt+1}] Error: {e}")
        logging.error("[Failure] Max retries reached.")
    return wrapper

def with_retries_async(fn, max_retries=3) -> callable:
    async def wrapper(*args, **kwargs) -> callable:
        for attempt in range(max_retries):
            try:
                return await fn(*args, **kwargs)
            except Exception as e:
                logging.warning(f"[Async Retry {attempt+1}] Error: {e}")
                await asyncio.sleep(1)  # optional backoff
        logging.error("[Async Failure] Max retries reached.")
    return wrapper

# job error listener
def job_error_listener(event) -> None:
    logging.error(f"[ALERT] Job {event.job_id} failed with: {event.exception}")


def create_sync_scheduler() -> BackgroundScheduler:
    """Create a synchronous scheduler.

    Returns:
        BackgroundScheduler: The created synchronous scheduler.
    """
    scheduler = BackgroundScheduler()
    # load_jobs_from_job_configs(scheduler)
    return scheduler


def create_async_scheduler() -> AsyncIOScheduler:
    """Create an asynchronous scheduler.

    Returns:
        AsyncIOScheduler: The created asynchronous scheduler.
    """
    scheduler = AsyncIOScheduler()

    for job_cfg in JOB_CONFIGS:
        platform = job_cfg["platform"]
        if platform != "discord":
            continue  # for now only handle async (Discord) here

        job_name = job_cfg["name"]
        cron = job_cfg.get("cron")
        params = job_cfg["params"]

        async def discord_job(params=params):
            crawler = DiscordCrawler(**params, snapshot_mode=True)
            await crawler.async_run()

        job_func = with_retries_async(discord_job)
        scheduler.add_job(job_func, CronTrigger(**cron), id=job_name, name=job_name)
        logging.info(f"[AsyncScheduler] Registered Discord job '{job_name}'")

    # add job error listener
    scheduler.add_listener(job_error_listener, EVENT_JOB_ERROR)
    return scheduler


def load_jobs_from_job_configs(scheduler) -> None:
    """Load jobs from the job configuration.

    Args:
        scheduler (BackgroundScheduler): The scheduler to load jobs into.
    """
    for job_cfg in JOB_CONFIGS:
        job_name = job_cfg["name"]
        platform = job_cfg["platform"]
        params = job_cfg["params"]
        cron = job_cfg.get("cron")

        # wrap Discord jobs in a separate function to avoid blocking the main thread
        # as discord_crawler uses asyncio
        if platform == "discord":
            def discord_wrapper(params=params):
                async def run_discord():
                    crawler = DiscordCrawler(**params, snapshot_mode=True)
                    await crawler.async_run()
                asyncio.run(with_retries_async(run_discord)())

            scheduler.add_job(discord_wrapper, CronTrigger(**cron), id=job_name, name=job_name)
            logging.info(f"[SyncScheduler] Registered Discord job '{job_name}'")
            continue

        if platform not in PLATFORM_FACTORY:
            logging.warning(f"[SyncScheduler] Unknown platform: {platform}")
            continue

        crawler = PLATFORM_FACTORY[platform](params)
        job_func = with_retries(crawler.run)
        scheduler.add_job(
            func=job_func,
            trigger=CronTrigger(**cron),
            id=job_name,
            name=job_name
        )
        logging.info(f"[SyncScheduler] Scheduled job '{job_name}' with cron: {cron}")

    # add job error listener
    scheduler.add_listener(job_error_listener, EVENT_JOB_ERROR)