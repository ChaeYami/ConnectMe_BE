from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from meeting.models import Meeting

from meeting.serializer import MeetingStatusupdateSerializer

from datetime import datetime
import pytz


def job():
    time_zone = pytz.timezone("Asia/Seoul")
    now = datetime.now(time_zone)
    now_datetime = now.strftime("%Y-%m-%d %H:%M")
    meetings = Meeting.objects.all()
    for meeting in meetings:
        end_meeting = meeting.meeting_at
        if end_meeting == now_datetime:
            serializer = MeetingStatusupdateSerializer(
                meeting, {"meeting_status": "모집종료"}
            )
            if serializer.is_valid():
                serializer.save(meeting_status="모집종료")


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job, max_instances=1, trigger=IntervalTrigger(minutes=1))
    scheduler.start()
