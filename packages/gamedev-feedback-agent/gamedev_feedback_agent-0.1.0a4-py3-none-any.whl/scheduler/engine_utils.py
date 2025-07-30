# engine utilities

from apscheduler.triggers.cron import CronTrigger
from scheduler.jobs import PLATFORM_FACTORY
from crawlers.discord_crawler import DiscordCrawler
import logging
from scheduler.engine import with_retries, with_retries_async


# job_id is the unique identifier for the job, while job_name is a human-readable name 
# technically, for parameters passing in, job_id or job_name should be the same
# as they are passed in to the get_job function which accepts either
# but for clarity, we separate them

# print and log
# interactive shell and cli use print for feedback, while logging is used for internal tracking
def print_and_log(message):
    print(message)
    logging.info(message)
    
def print_and_log_warning(message):
    print(message)
    logging.warning(message)

def print_and_log_error(message):
    print(message)
    logging.error(message)
    
    
# get a job by ID or name
def get_job(scheduler, job_id_or_name) -> str:
    """Get a job by its ID or name.

    Args:
        scheduler (BackgroundScheduler): The scheduler to get the job from.
        job_id_or_name (str): The ID or name of the job to retrieve.

    Returns:
        str: the job id or None if not found
    """
    job = scheduler.get_job(job_id_or_name)
    if not job:
        print_and_log_warning(f"[Scheduler] Job '{job_id_or_name}' not found.")
    return job


# get a job by name
def get_job_by_name(scheduler, job_name) -> str:
    job = scheduler.get_job(job_name)
    if not job:
        print_and_log_warning(f"[Scheduler] Job '{job_name}' not found.")
    return job

# get job by ID
def get_job_by_id(scheduler, job_id) -> str:
    job = scheduler.get_job(job_id)
    if not job:
        print_and_log_warning(f"[Scheduler] Job with ID '{job_id}' not found.")
    return job


# get all jobs for a specific platform
def get_jobs_by_platform(scheduler, platform) -> list:
    """Get all jobs for a specific platform.
    Compares the job name with the platform name to filter jobs.
    
    Args:
        scheduler (BackgroundScheduler): The scheduler to get the jobs from.
        platform (str): The platform name to filter jobs by.

    Returns:
        list: A list of job IDs for the specified platform.
    """
    jobs = [job for job in scheduler.get_jobs() if job.name.startswith(platform)]
    if not jobs:
        print_and_log_warning(f"[Scheduler] No jobs found for platform '{platform}'.")
    return jobs


# remove a job by name
def remove_job(scheduler, job_name) -> None:
    """Remove a job from the scheduler by its name.

    Args:
        scheduler (BackgroundScheduler): The scheduler to remove the job from.
        job_name (str): The name of the job to remove.
    """
    job = get_job_by_name(scheduler, job_name)
    if job:
        scheduler.remove_job(job.id)
        print_and_log(f"[Scheduler] Removed job '{job_name}'.")
    else:
        print_and_log_warning(f"[Scheduler] Job '{job_name}' not found.")
       

# list all jobs in the scheduler
def list_jobs(scheduler) -> None:
    """List all jobs in the scheduler.

    Args:
        scheduler (BackgroundScheduler): The scheduler to list jobs from.
    """
    jobs = scheduler.get_jobs()
    if not jobs:
        print("[Scheduler] No jobs scheduled.")
    else:
        for job in jobs:
            print_and_log(f"[Scheduler] Job: {job.name} (ID: {job.id}) - Next run: {job.next_run_time}")


# pause a job
def pause_job(scheduler, job_name) -> None:
    """Pause a job in the scheduler.

    Args:
        scheduler (BackgroundScheduler): The scheduler to pause the job in.
        job_name (str): The name of the job to pause.
    """
    job = get_job_by_name(scheduler, job_name)
    if job:
        scheduler.pause_job(job.id)
        print_and_log(f"[Scheduler] Paused job '{job_name}'.")
    else:
        print_and_log_warning(f"[Scheduler] Job '{job_name}' not found.")


# resume a paused job
def resume_job(scheduler, job_name) -> None:
    """Resume a paused job in the scheduler.

    Args:
        scheduler (BackgroundScheduler): The scheduler to resume the job in.
        job_name (str): The name of the job to resume.
    """
    job = get_job_by_name(scheduler, job_name)
    if job:
        scheduler.resume_job(job.id)
        print_and_log(f"[Scheduler] Resumed job '{job_name}'.")
    else:
        print_and_log_warning(f"[Scheduler] Job '{job_name}' not found.")


# reschedule a job with a new cron schedule
def reschedule_job(scheduler, job_name, cron) -> None:
    """Reschedule a job with a new cron schedule.

    Args:
        scheduler (BackgroundScheduler): The scheduler to reschedule the job in.
        job_name (str): The name of the job to reschedule.
        cron (dict): The new cron schedule for the job.
    """
    job = get_job_by_name(scheduler, job_name)
    if job:
        scheduler.reschedule_job(job.id, trigger=CronTrigger(**cron))
        print_and_log(f"[Scheduler] Rescheduled job '{job_name}' with new cron: {cron}.")
    else:
        print_and_log_warning(f"[Scheduler] Job '{job_name}' not found.")


# Dynamically add a new job
def add_job_crawler(scheduler, job_cfg, is_async=False) -> None:
    """Add a new job to the scheduler.

    Args:
        scheduler (BackgroundScheduler): The scheduler to add the job to.
        job_cfg (dict): The configuration for the job.
        is_async (bool, optional): Whether the job is asynchronous. Defaults to False.
    """
    job_name = job_cfg["name"]
    platform = job_cfg["platform"]
    cron = job_cfg["cron"]
    params = job_cfg["params"]

    if is_async or platform == "discord":
        # If you later want to dynamically add Discord jobs
        async def discord_job():
            crawler = DiscordCrawler(**params, snapshot_mode=True)
            await crawler.async_run()

        from scheduler.engine import with_retries_async  # import here to avoid circular import
        job_func = with_retries_async(discord_job)
        scheduler.add_job(job_func, CronTrigger(**cron), id=job_name, name=job_name)
    else:
        crawler = PLATFORM_FACTORY[platform](params)
        from scheduler.engine import with_retries
        job_func = with_retries(crawler.run)
        scheduler.add_job(job_func, CronTrigger(**cron), id=job_name, name=job_name)
    
    print_and_log(f"[Scheduler] Added job '{job_name}' for platform '{platform}' with cron: {cron}.")


# run a job immediately
def run_job_now(scheduler, job_name) -> None:
    """Run a job immediately.

    Args:
        scheduler (BackgroundScheduler): The scheduler to run the job in.
        job_name (str): The name of the job to run.
    """
    job = get_job_by_name(scheduler, job_name)
    if job:
        print_and_log(f"[Scheduler] Running job '{job_name}' immediately.")
        job.func()  # Call the job function directly
    else:
        print_and_log_warning(f"[Scheduler] Job '{job_name}' not found.")
        

# clear all jobs in the scheduler
def clear_all_jobs(scheduler) -> None:
    """Clear all jobs in the scheduler.

    Args:
        scheduler (BackgroundScheduler): The scheduler to clear jobs from.
    """
    jobs = scheduler.get_jobs()
    for job in jobs:
        scheduler.remove_job(job.id)
    print_and_log(f"[Scheduler] Cleared all jobs.")
    
    
def add_job(scheduler, job_name, job_func, cron) -> None:
    """Add a job to the scheduler.

    Args:
        scheduler (BackgroundScheduler): The scheduler to add the job to.
        job_name (str): The name of the job.
        job_func (callable): The function to run for the job.
        cron (dict): The cron schedule for the job.
    """
    if not job_name or not job_func or not cron:
        print_and_log_error("[Scheduler] Job name, function, and cron schedule must be provided.")
        return
    
    # check cron format
    if not isinstance(cron, dict):
        print_and_log_error("[Scheduler] Cron schedule must be a dictionary.")
        return

    # check if the job already exists
    existing_job = scheduler.get_job(job_name)
    if existing_job:
        print_and_log_warning(f"[Scheduler] Job '{job_name}' already exists.")
        return

    # check job_func is callable
    if not callable(job_func):
        print_and_log_error(f"[Scheduler] Job function '{job_func}' is not callable.")
        return
    
    # wrap the job function with retries
    from scheduler.engine import with_retries
    job_func = with_retries(job_func)
    
    try:
    # add the job to the scheduler
        scheduler.add_job(
            func=job_func,
            trigger=CronTrigger(**cron),
            id=job_name,
            name=job_name
        )
    except Exception as e:
        print_and_log_error(f"[Scheduler] Failed to add job '{job_name}': {e}")
        return