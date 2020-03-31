from utils.jobs import user_monitor, test
from flask_apscheduler import APScheduler


def start_jobs():
    scheduler = APScheduler()
    scheduler.add_job(func=user_monitor, id='1', trigger='interval', seconds=5, replace_existing=True)
    scheduler.add_job(func=test, id='2', trigger='interval', seconds=5, replace_existing=True)
    scheduler.start()
