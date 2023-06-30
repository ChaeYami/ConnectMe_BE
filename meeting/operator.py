from apscheduler.schedulers.background import BackgroundScheduler

from meeting.models import Meeting

from meeting.serializer import MeetingStatusupdateSerializer

from datetime import datetime

def job():
    now = datetime.now()
    now_datetime = now.strftime('%Y-%m-%d %I:%M %p')
    meetings = Meeting.objects.all()
    for meeting in meetings:
        end_meeting = meeting.meeting_at 
        if end_meeting == now_datetime:
            serializer = MeetingStatusupdateSerializer(meeting, {"meeting_status":"모집종료"})
            if serializer.is_valid():
                serializer.save(meeting_status="모집종료")

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job,'interval', minutes=10, id='check_meeting_at')
    scheduler.start()



