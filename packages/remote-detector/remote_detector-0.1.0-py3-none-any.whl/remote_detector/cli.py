import click
import multiprocessing
import os
import psutil
import sys
import datetime
import getpass

from .detector import run_detection, detect_remote_tools
from .logger import get_logger
from .erp import ERPClient

logger = get_logger()

@click.group()
def cli():
    pass

@cli.command()
@click.option('--duration', default=3, type=float, help='Duration in hours')
def start(duration):
    # Prompt for ERP credentials
    print("Login to IIITA ERP to start session:")
    uid = input("Username (UID): ")
    pwd = getpass.getpass("Password: ")
    batch = input("Batch (e.g. 2025): ")
    credentials = {
        'myBatch': batch,
        'uid': uid,
        'pwd': pwd,
        'norobo': "1"
    }
    erp_client = ERPClient()
    if not erp_client.login(credentials):
        print("ERP login failed. Please check your credentials.")
        sys.exit(1)
    print("ERP login successful! Fetching ERP details...")
    # Fetch dashboard content and ERP details
    try:
        response = erp_client.session.get(erp_client.base_url)
        # Debug: log the first part of the HTML to check if login worked
        with open("erp_debug.html", "w", encoding="utf-8") as f:
            f.write(response.text[:2000])
        print("ERP dashboard HTML saved to erp_debug.html for inspection.")
        courses = erp_client.get_all_courses(response.text)
        summaries = erp_client.get_semester_summary(response.text)
        erp_details = {
            "uid": uid,
            "batch": batch,
            "courses": courses,
            "semester_summaries": summaries
        }
        logger.info({"event": "erp_details", "details": erp_details, "erp_username": uid})
        print(f"ERP details fetched and logged for UID {uid}.")
        # Immediately detect and log current remote tools
        detected_now = detect_remote_tools()
        for d in detected_now:
            app_name = d.get('tool') or (d.get('details', {}).get('name'))
            logger.info({
                "system_username": getpass.getuser(),
                "erp_username": uid,
                "app_name": app_name,
                "timestamp": datetime.datetime.now().isoformat()
            })
        print("Initial detected applications have been logged.")
    except Exception as e:
        logger.warning({"event": "erp_details_error", "error": str(e), "erp_username": uid})
        print(f"Warning: Could not fetch or log ERP details: {e}")
    pid_file = 'remote_detector.pid'
    if os.path.exists(pid_file):
        with open(pid_file, 'r') as f:
            pid = int(f.read())
        if psutil.pid_exists(pid):
            logger.info({"event": "status", "message": "Already running", "erp_username": uid})
            print("Already running")
            return
    process = multiprocessing.Process(target=run_detection, args=(duration,))
    process.daemon = True
    process.start()
    with open(pid_file, 'w') as f:
        f.write(str(process.pid))
    logger.info({"event": "start", "pid": process.pid, "erp_username": uid})
    print(f"Started with PID {process.pid}")

@cli.command()
def status():
    pid_file = 'remote_detector.pid'
    if not os.path.exists(pid_file):
        print("Not running")
        return
    with open(pid_file, 'r') as f:
        pid = int(f.read())
    if psutil.pid_exists(pid):
        print(f"Running with PID {pid}")
    else:
        print("Not running")
        os.remove(pid_file)

@cli.command()
@click.option('--duration', default=3, type=float, help='Duration in hours')
def debug(duration):
    run_detection(duration)

if __name__ == '__main__':
    cli() 