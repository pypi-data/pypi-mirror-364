import argparse
import ast
import os
import signal
import sys
from sys import stdout, stderr
import subprocess
from scheduler.engine import create_sync_scheduler
from scheduler.engine_utils import (
    list_jobs, pause_job, resume_job, remove_job,
    get_job_by_name, add_job_crawler, run_job_now, clear_all_jobs, add_job
)
import psutil
import time
import json
from datetime import datetime

from cli.commands.report_cmd import handle_brief


PID_FILE = ".scheduler.pid"


# def is_scheduler_running():
#     if not os.path.exists(PID_FILE):
#         print("[Scheduler] PID file does not exist. Scheduler is not running.")
#         return False, None
#     try:
#         with open(PID_FILE, "r") as f:
#             pid = int(f.read().strip())
#         p = psutil.Process(pid)
#         print(f"[Scheduler] Checking if process {pid} is running... : " f"{p.is_running()}")
#         if p.is_running() and "python" in p.name().lower():
#             return True, p
#     except Exception as e:
#         print(f"[Scheduler] Error checking process: {e}")
#     return False, None


# def start_scheduler():
#     running, _ = is_scheduler_running()
#     if running:
#         print("[Scheduler] Already running.")
#         return

#     if os.path.exists(PID_FILE):
#         os.remove(PID_FILE)

#     script_path = os.path.abspath("run_scheduler.py")
#     print(f"[Debug] Launching: {script_path}")

#     try:
#         proc = subprocess.Popen(
#             [sys.executable, script_path],
#             stdout=subprocess.DEVNULL,
#             stderr=subprocess.PIPE,
#             stdin=subprocess.DEVNULL,
#             creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0)
#         )

#         # Wait briefly to check if it crashes early
#         time.sleep(1)

#         if proc.poll() is not None:
#             print(f"[Scheduler] Process exited with code {proc.returncode}")
#             error_output = proc.stderr.read().decode()
#             print("[Scheduler STDERR]")
#             print(error_output)
#             return  # Don't write .pid if it crashed

#         with open(PID_FILE, "w") as f:
#             f.write(str(proc.pid))

#         print(f"[Scheduler] Started with PID {proc.pid}.")

#     except Exception as e:
#         print(f"[Error] Failed to start scheduler: {e}")
        

# def stop_scheduler():
#     running, process = is_scheduler_running()
#     if not running:
#         print("[Scheduler] Not running.")
#         return
#     try:
#         process.terminate()
#         process.wait(timeout=5)
#         print("[Scheduler] Stopped.")
#     except Exception as e:
#         print(f"[Error] Could not stop scheduler: {e}")
#     finally:
#         if os.path.exists(PID_FILE):
#             os.remove(PID_FILE)


# def scheduler_status():
#     running, process = is_scheduler_running()
#     if running:
#         print(f"[Scheduler] Running (PID {process.pid})")
#     else:
#         print("[Scheduler] Not running.")


# Global scheduler instance for interactive commands (not for daemon)
scheduler = create_sync_scheduler()
scheduler.start()


def handle(args) -> None:
    """Handle the scheduler command.

    Args:
        args (list[str]): The arguments for the command.
    """
    parser = argparse.ArgumentParser(prog="scheduler", description="Manage and schedule background crawling jobs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    subparsers.add_parser("list", help="List all scheduled jobs")

    # pause
    pause_parser = subparsers.add_parser("pause", help="Pause a scheduled job")
    pause_parser.add_argument("job_id", help="ID of the job to pause")

    # resume
    resume_parser = subparsers.add_parser("resume", help="Resume a paused job")
    resume_parser.add_argument("job_id", help="ID of the job to resume")

    # delete
    delete_parser = subparsers.add_parser("delete", help="Delete a job from the scheduler")
    delete_parser.add_argument("job_id", help="ID of the job to delete")

    # run_now (not implemented directly but stubbed)
    run_now_parser = subparsers.add_parser("run_now", help="Run a job immediately (not implemented)")
    run_now_parser.add_argument("job_id", help="ID of the job to run immediately")

    # clear
    subparsers.add_parser("clear", help="Clear all scheduled jobs")

    # status
    subparsers.add_parser("status", help="Show scheduler status")

    # start/stop
    # subparsers.add_parser("start", help="Start the scheduler process")
    # subparsers.add_parser("stop", help="Stop the scheduler process")

    # add
    add_parser = subparsers.add_parser("add", help="Add a new scheduled job")
    add_parser.add_argument("--path", required=True, help="Path to the job configuration file")

    # crawling (recurring with interval or presets)
    crawl_parser = subparsers.add_parser("crawling", help="Schedule recurring crawling jobs")
    crawl_parser.add_argument("--platform", help="Platform for the job")
    # platform-specific arguments
    crawl_parser.add_argument("--subreddits", help="Subreddits to crawl (comma-separated)")
    crawl_parser.add_argument("--post_id", help="Post ID for the Reddit crawler")
    crawl_parser.add_argument("--post_url", help="Post URL for the Reddit crawler")

    crawl_parser.add_argument("--app_id", help="App ID for the steam crawler")
    
    crawl_parser.add_argument("--channels", help="Discord channel IDs (comma-separated)")

    crawl_parser.add_argument("--start_time", help="Start time in 'YYYY-MM-DD HH:MM'")
    crawl_parser.add_argument("--end_time", help="End time in 'YYYY-MM-DD HH:MM'")
    crawl_parser.add_argument("--interval", help="Interval like '6h', '2h'")
    crawl_parser.add_argument("--daily_at", help="Daily run time like '14:00'")
    crawl_parser.add_argument("--weekly", action="store_true", help="Weekly run")
    crawl_parser.add_argument("--day", help="Day of week if weekly")
    #crawl_parser.add_argument("--between", help="Time window like '09:00-17:00'")
    crawl_parser.set_defaults(func=handle_crawling)
    
    
    # brief job
    brief_parser = subparsers.add_parser("brief", help="Run a brief report job")
    brief_parser.add_argument("--platform", nargs="+", help="Platform(s) for the brief report job")
    brief_parser.add_argument("--daily_at", help="Daily run time like '14:00'")
    brief_parser.add_argument("--weekly", action="store_true", help="Run weekly brief report")
    brief_parser.add_argument("--day", help="Day of week if weekly")

    try:
        parsed = parser.parse_args(args)
        cmd = parsed.command

        if cmd == "list":
            list_jobs(scheduler)

        elif cmd == "pause":
            pause_job(scheduler, parsed.job_id)

        elif cmd == "resume":
            resume_job(scheduler, parsed.job_id)

        elif cmd == "delete":
            remove_job(scheduler, parsed.job_id)

        elif cmd == "run_now":
            run_job_now(scheduler, parsed.job_id)
            
        elif cmd == "clear":
            confirm = input("[Scheduler] Are you sure you want to clear all jobs? (y/N): ").strip().lower()
            if confirm == 'y':
                clear_all_jobs(scheduler)
                # print("[Scheduler] Cleared all jobs.") # printed in clear_all_jobs
            else:
                print("[Scheduler] Clear operation cancelled.")

        elif cmd == "status":
            # scheduler_status()
            list_jobs(scheduler)

        # elif cmd == "start":
        #     start_scheduler()

        # elif cmd == "stop":
        #     stop_scheduler()

        elif cmd == "add":
            if not os.path.exists(parsed.path):
                print(f"[Error] Job configuration file '{parsed.path}' does not exist.")
                return
            try:
                with open(parsed.path, "r") as f:
                    job_cfg = json.load(f)
                add_job_crawler(scheduler, job_cfg)
                print(f"[Scheduler] Added job from {parsed.path}")
            except Exception as e:
                print(f"[Error] Failed to add job: {e}")
                
        elif cmd == "crawling":
            handle_crawling(parsed)
        
        elif cmd == "brief":
            handle_brief_job(parsed)

    except SystemExit:
        pass  # argparse help or error
    except Exception as e:
        print(f"[Scheduler Error] {e}")



def handle_crawling(parsed: argparse.Namespace) -> None:
    """Handle the crawling job.

    Args:
        parsed (argparse.Namespace): The parsed command-line arguments.
    """
    print("[Scheduler] Handling crawling job...")
    if not parsed.platform:
        print("[Error] Must specify --platform for crawling job")
        return
    if parsed.platform not in ["reddit", "steam", "discord"]:
        print(f"[Error] Unsupported platform: {parsed.platform}")
        return
    
    # job name generation
    job_name = f"{parsed.platform}_"
    if parsed.platform == "reddit":
        if parsed.subreddits:
            job_name += "reddit_" + "_".join(parsed.subreddits.split(","))
        elif parsed.post_id:
            job_name += f"reddit_post_{parsed.post_id}"
        elif parsed.post_url:
            job_name += f"reddit_post_{parsed.post_url.split('/')[-1]}"
        else:
            print("[Error] Must specify --subreddits, --post_id, or --post_url for Reddit job")
            return
    elif parsed.platform == "steam":
        if parsed.app_id:
            job_name += f"steam_app_{parsed.app_id}"
        else:
            print("[Error] Must specify --app_id for Steam job")
            return
    elif parsed.platform == "discord":
        if parsed.channels:
            job_name += "discord_" + "_".join(parsed.channels.split(","))
        else:
            print("[Error] Must specify --channels for Discord job")
            return
    job_name += f"_{int(time.time())}"

    if get_job_by_name(scheduler, job_name):
        print(f"[Scheduler] Job '{job_name}' already exists.")
        return

    # Default: use --interval for simple cron
    cron_dict = {}
    if parsed.interval:
        # Convert "6h" → every 6 hours
        if "h" in parsed.interval:
            hour = parsed.interval.replace("h", "")
            cron_dict["minute"] = "0"
            cron_dict["hour"] = f"*/{hour}"
        elif "m" in parsed.interval:
            minute = parsed.interval.replace("m", "")
            cron_dict["minute"] = f"*/{minute}"
        else:
            print("[Error] Invalid interval format")
            return

    elif parsed.daily_at:
        hour, minute = parsed.daily_at.split(":")
        cron_dict["hour"] = hour
        cron_dict["minute"] = minute

    elif parsed.weekly:
        cron_dict["day_of_week"] = parsed.day or "mon"
        cron_dict["hour"] = "10"
        cron_dict["minute"] = "0"
    else:
        print("[Error] Must provide one of: --interval, --daily-at, or --weekly")
        return
        
    if parsed.start_time or parsed.end_time:
        # check format "YYYY-MM-DD HH:MM"
        print("[DEBUG] start_time:", parsed.start_time)
        if parsed.start_time:
            try:
                start_time = datetime.strptime(parsed.start_time.strip("'\""), "%Y-%m-%d %H:%M")
                cron_dict["start_date"] = start_time
            except ValueError:
                print("[Error] Invalid start_time format. Use 'YYYY-MM-DD HH:MM'")
                return
        if parsed.end_time:
            try:
                end_time = datetime.strptime(parsed.end_time.strip("'\""), "%Y-%m-%d %H:%M")
                cron_dict["end_date"] = end_time
            except ValueError:
                print("[Error] Invalid end_time format. Use 'YYYY-MM-DD HH:MM'")
                return
        
    

    params = {}
    if parsed.subreddits:
        params["subreddits"] = parsed.subreddits.split(",")
    if parsed.post_id:
        params["post_id"] = parsed.post_id
    if parsed.post_url:
        params["post_url"] = parsed.post_url
    if parsed.app_id:
        params["app_id"] = parsed.app_id
    if parsed.channels:
        params["channel_ids"] = parsed.channels.split(",")

    job_cfg = {
        "name": job_name,
        "platform": parsed.platform,
        "cron": cron_dict,
        "params": params
    }

    add_job_crawler(scheduler, job_cfg)
    print(f"[Scheduler] Added crawling job '{job_name}'")
    
    
    

def handle_brief_job(parsed: argparse.Namespace) -> None:
    if not parsed.daily_at and not parsed.weekly:
        print("[Error] Must specify --daily_at or --weekly for brief report job")
        return
    
    if parsed.weekly and not parsed.day:
        print("[Error] Must specify --day for weekly brief report job")
        return
    
    # daily job
    from argparse import Namespace
    if parsed.daily_at:
        print(f"[Scheduler] Scheduling daily brief report job at {parsed.daily_at}")
        hour, minute = parsed.daily_at.split(":")
        cron_dict = {
            "hour": hour,
            "minute": minute
        }
        job_name = f"brief_daily_{hour}_{minute}"
        if scheduler.get_job(job_name):
            print(f"[Scheduler] Daily brief job '{job_name}' already exists.")
            return
        
        brief_args = Namespace(
            since=None,
            daily=True,
            weekly=None,
            platform=None
        )

        job_func = lambda: handle_brief(brief_args)
        add_job(scheduler, job_name, job_func, cron_dict)
    # weekly job
    if parsed.weekly:
        print(f"[Scheduler] Scheduling weekly brief report job on {parsed.day}, default at 10:00")
        cron_dict = {
            "day_of_week": parsed.day,
            "hour": "10",
            "minute": "0"
        }
        job_name = f"brief_weekly_{parsed.day}"
        if scheduler.get_job(job_name):
            print(f"[Scheduler] Weekly brief job '{job_name}' already exists.")
            return

        brief_args = Namespace(
            since=None,
            daily=None,
            weekly=True,
            platform=None
        )

        job_func = lambda: handle_brief(brief_args)
        add_job(scheduler, job_name, job_func, cron_dict)