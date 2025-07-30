from scheduler.engine import create_sync_scheduler, create_async_scheduler, load_jobs_from_job_configs, with_retries, with_retries_async
import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock, ANY
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR
from scheduler.engine import job_error_listener
from scheduler import engine_utils



FAKE_JOB_CONFIGS = [
    {
        "name": "reddit_job",
        "platform": "reddit",
        "params": {"subreddits": ["test"]},
        "cron": {"hour": "1"}
    },
    {
        "name": "discord_job",
        "platform": "discord",
        "params": {"channel_ids": ["123"], "token": "abc"},
        "cron": {"minute": "0"}
    },
    {
        "name": "unknown_job",
        "platform": "unknown",
        "params": {},
        "cron": {"minute": "30"}
    }
]

FAKE_PLATFORM_FACTORY = {
    "reddit": lambda p: MagicMock(run=MagicMock()),
    "discord": lambda p: MagicMock(run=MagicMock())
}



# 1. test scheduler engine initialization
def test_scheduler_engine_initialization():

    # Test sync scheduler creation
    sync_scheduler = create_sync_scheduler()
    assert sync_scheduler is not None

    # Test async scheduler creation
    async_scheduler = create_async_scheduler()
    assert async_scheduler is not None
    
    
# 2. test load jobs from job configs sync
@patch("scheduler.engine.PLATFORM_FACTORY", FAKE_PLATFORM_FACTORY)
@patch("scheduler.engine.JOB_CONFIGS", FAKE_JOB_CONFIGS)
@patch("scheduler.engine.with_retries_async")
@patch("scheduler.engine.DiscordCrawler")
def test_load_jobs_from_job_configs(
    mock_discord, mock_with_retries_async
):
    scheduler = MagicMock()

    # Prevent actual async run
    mock_with_retries_async.return_value.return_value = AsyncMock()

    load_jobs_from_job_configs(scheduler)

    # Two jobs should be added: reddit and discord
    assert scheduler.add_job.call_count == 2

    job_ids = [call.kwargs.get("id") or call.args[1] for call in scheduler.add_job.call_args_list]
    assert "reddit_job" in job_ids
    assert "discord_job" in job_ids
    assert "unknown_job" not in job_ids

    # Check listener added
    scheduler.add_listener.assert_called_once_with(ANY, EVENT_JOB_ERROR)
    
# 3. test with_retries and with_retries_async decorators
def test_with_retries_all(monkeypatch):
    # Test sync success
    mock_fn = MagicMock(return_value=42)
    wrapped = with_retries(mock_fn)
    result = wrapped()
    assert result == 42
    mock_fn.assert_called_once()

    # Test sync failure
    mock_fn_fail = MagicMock(side_effect=Exception("fail"))
    wrapped_fail = with_retries(mock_fn_fail, max_retries=2)
    with patch("logging.warning") as mock_warn, patch("logging.error") as mock_err:
        result = wrapped_fail()
        assert result is None
        assert mock_fn_fail.call_count == 2
        mock_warn.assert_called()
        mock_err.assert_called_once()

    # Test async success
    async def async_fn():
        return "ok"
    wrapped_async = with_retries_async(async_fn)
    result = asyncio.run(wrapped_async())
    assert result == "ok"

    # Test async failure
    async def async_fn_fail():
        raise Exception("fail")
    wrapped_async_fail = with_retries_async(async_fn_fail, max_retries=2)
    with patch("logging.warning") as mock_warn, patch("logging.error") as mock_err:
        result = asyncio.run(wrapped_async_fail())
        assert result is None
        assert mock_warn.call_count == 2
        mock_err.assert_called_once()


# 4. test job error listener
def test_job_error_listener():
    with patch("logging.error") as mock_error:
        event = MagicMock(job_id="test_job", exception=Exception("test error"))
        job_error_listener(event)
        mock_error.assert_called_once_with("[ALERT] Job test_job failed with: test error")
        

# 5. test engine utils functions
def test_engine_utils_functions():
    scheduler = MagicMock()
    job = MagicMock(id="job1", name="job1", next_run_time="2024-01-01 00:00:00")
    scheduler.get_job.side_effect = lambda x: job if x in ["job1", "job_name"] else None
    scheduler.get_jobs.return_value = [job]
    
    # Test get_job
    assert engine_utils.get_job(scheduler, "job1") == job
    assert engine_utils.get_job(scheduler, "not_exist") is None

    # Test get_job_by_name
    assert engine_utils.get_job_by_name(scheduler, "job_name") == job
    assert engine_utils.get_job_by_name(scheduler, "not_exist") is None

    # Test get_job_by_id
    assert engine_utils.get_job_by_id(scheduler, "job1") == job
    assert engine_utils.get_job_by_id(scheduler, "not_exist") is None

    # Test get_jobs_by_platform
    job.name = "reddit_job"
    scheduler.get_jobs.return_value = [job]
    jobs = engine_utils.get_jobs_by_platform(scheduler, "reddit")
    assert jobs == [job]
    scheduler.get_jobs.return_value = []
    jobs = engine_utils.get_jobs_by_platform(scheduler, "reddit")
    assert jobs == []

    # Test remove_job
    scheduler.get_jobs.return_value = [job]
    scheduler.get_job.side_effect = lambda x: job if x == "job1" else None
    engine_utils.remove_job(scheduler, "job1")
    scheduler.remove_job.assert_called_with("job1")

    # Test list_jobs
    scheduler.get_jobs.return_value = [job]
    engine_utils.list_jobs(scheduler)
    scheduler.get_jobs.return_value = []
    engine_utils.list_jobs(scheduler)

    # Test pause_job and resume_job
    scheduler.get_job.side_effect = lambda x: job if x == "job1" else None
    engine_utils.pause_job(scheduler, "job1")
    scheduler.pause_job.assert_called_with("job1")
    engine_utils.resume_job(scheduler, "job1")
    scheduler.resume_job.assert_called_with("job1")

    # Test reschedule_job
    scheduler.get_job.side_effect = lambda x: job if x == "job1" else None
    cron = {"minute": "0"}
    engine_utils.reschedule_job(scheduler, "job1", cron)
    assert scheduler.reschedule_job.called

    # Test add_job_crawler (sync)
    job_cfg = {
        "name": "reddit_job",
        "platform": "reddit",
        "cron": {"minute": "0"},
        "params": {}
    }
    with patch("scheduler.engine.PLATFORM_FACTORY", FAKE_PLATFORM_FACTORY):
        engine_utils.add_job_crawler(scheduler, job_cfg, is_async=False)
        assert scheduler.add_job.called

    # Test run_job_now
    scheduler.get_job.side_effect = lambda x: job if x == "job1" else None
    job.func = MagicMock()
    engine_utils.run_job_now(scheduler, "job1")
    job.func.assert_called_once()

    # Test clear_all_jobs
    scheduler.get_jobs.return_value = [job]
    engine_utils.clear_all_jobs(scheduler)
    scheduler.remove_job.assert_called_with(job.id)


# 6. test job creation with retries
@patch("scheduler.engine.with_retries")
def test_add_job_crawler_with_retries(mock_with_retries):
    mock_with_retries.return_value = MagicMock()
    scheduler = MagicMock()
    job_cfg = {
        "name": "test_job",
        "platform": "reddit",
        "cron": {"minute": "0"},
        "params": {}
    }
    engine_utils.add_job_crawler(scheduler, job_cfg, is_async=False)
    mock_with_retries.assert_called_once()
    
    
# 7. test job creation with retries async
@patch("scheduler.engine.with_retries_async")
def test_add_job_crawler_with_retries_async(mock_with_retries_async):
    mock_with_retries_async.return_value = AsyncMock()
    scheduler = MagicMock()
    job_cfg = {
        "name": "test_job",
        "platform": "discord",
        "cron": {"minute": "0"},
        "params": {}
    }
    engine_utils.add_job_crawler(scheduler, job_cfg, is_async=True)
    mock_with_retries_async.assert_called_once()
    

# 8. test job createion in jobs.py
@patch("scheduler.jobs.PLATFORM_FACTORY", FAKE_PLATFORM_FACTORY)
@patch("scheduler.jobs.RedditCrawler")
@patch("scheduler.jobs.SteamCrawler")
@patch("scheduler.jobs.DiscordCrawler")
def test_job_creation(mock_discord, mock_steam, mock_reddit):
    from scheduler.jobs import create_reddit_job, create_steam_job, create_discord_job

    # Test Reddit job creation
    reddit_params = {"subreddits": ["test"]}
    reddit_job = create_reddit_job(reddit_params)
    assert reddit_job is not None
    mock_reddit.assert_called_once_with(**reddit_params)

    # Test Steam job creation
    steam_params = {"app_ids": [12345]}
    steam_job = create_steam_job(steam_params)
    assert steam_job is not None
    mock_steam.assert_called_once_with(**steam_params)

    # Test Discord job creation
    discord_params = {"channel_ids": ["123"], "token": "abc"}
    discord_job = create_discord_job(discord_params)
    assert discord_job is not None
    mock_discord.assert_called_once_with(**discord_params)
    
    
# 9. test engine async job creation from job configs
def test_create_async_scheduler_from_job_configs():
    with patch("scheduler.engine.JOB_CONFIGS", FAKE_JOB_CONFIGS):
        async_scheduler = create_async_scheduler()
        assert async_scheduler is not None

        # Check if jobs are registered correctly
        job_ids = [job.id for job in async_scheduler.get_jobs()]
        assert "discord_job" in job_ids
        assert "reddit_job" not in job_ids  # Reddit is not async
        assert "unknown_job" not in job_ids  # Unknown platform should be ignored

        # Check if the Discord job is scheduled correctly
        discord_job = async_scheduler.get_job("discord_job")
        assert discord_job is not None
        assert isinstance(discord_job.trigger, CronTrigger)