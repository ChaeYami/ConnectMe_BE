from django.contrib import admin
from .models import *


admin.site.register(Meeting)
admin.site.register(MeetingComment)
admin.site.register(MeetingCommentReply)
admin.site.register(MeetingImage)
