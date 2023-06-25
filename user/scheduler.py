from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from user.models import Blacklist, Report
import pytz
from django.utils import timezone
from datetime import datetime, timedelta


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(task, "cron", minute="0")  # 서비스용 코드 - 매시 00분에 실행
    # scheduler.add_job(
    #     task, max_instances=1, trigger=IntervalTrigger(seconds=30)
    # )  # 테스트용 코드 - 30초마다 실행
    scheduler.start()


# 임시차단 해제
def task():
    time_zone = pytz.timezone("Asia/Seoul")
    current_time = datetime.now(time_zone)

    blacklist = Blacklist.objects.all()
    for black in blacklist:
        unblock_time = black.blocked_at.astimezone(time_zone) + timedelta(hours=24)
        if black.blocked_user.is_blocked and current_time >= unblock_time:
            black.blocked_user.is_blocked = False
            black.blocked_user.is_active = True
            black.blocked_user.warning = 0
            black.blocked_user.save()
            Report.objects.filter(reported_user=black.blocked_user).delete()
    print("임시차단 해제 로직 완료")
