from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from django.utils import timezone
from django.db.models import Q

from datetime import datetime, timedelta, date

import pytz

from user.models import Blacklist, Report, InactiveUser


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(task, "cron", minute="0")  # 서비스용 코드 - 매시 00분에 실행
    scheduler.add_job(account_del_task, "cron", hour="0")  # 서비스용 코드 - 매일 00시 실행
    # scheduler.add_job(
    #     task, max_instances=1, trigger=IntervalTrigger(seconds=30)
    # )  # 테스트용 코드 - 30초마다 실행
    # scheduler.add_job(
    #     account_del_task, max_instances=1, trigger=IntervalTrigger(seconds=30)
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


def account_del_task():
    inactive_list = InactiveUser.objects.all()

    if inactive_list.exists():
        for inactive_one in inactive_list:
            inactivated_at = inactive_one.inactivated_at
            reactivate_day = inactivated_at.date() + timedelta(days=30)
            current_date = date.today()
            
            if reactivate_day < current_date:
                # 해당 날짜가 지났음
                inactive_one.inactive_user.delete() 
                print("지워짐")               
            else:
                # 해당 날짜가 아직 지나지 않음
                pass
    else:
        pass