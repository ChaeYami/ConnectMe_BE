from django.db import models

from user.models import User
# Create your models here.

class Meeting(models.Model):
    user = models.ForeignKey(User, verbose_name="작성자", on_delete=models.CASCADE)
    title = models.CharField(verbose_name="제목", max_length=50)
    content = models.TextField(verbose_name="모임내용",)
    created_at = models.DateTimeField(verbose_name="작성일" , auto_now_add=True,)
    updated_at = models.DateTimeField(verbose_name="수정일" , auto_now=True)
    bookmark = models.ManyToManyField(User, verbose_name="북마크", blank=True, related_name="bookmark_meeting")

class MeetingComment(models.Model):
    user = models.ForeignKey(User, verbose_name="작성자", on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, verbose_name="미팅", on_delete=models.CASCADE, related_name="comment") #Nested Serializer 사용을 위해 related_name 지정
    content = models.TextField(verbose_name="댓글내용")
    created_at = models.DateTimeField(verbose_name="작성일" , auto_now_add=True,)
    updated_at = models.DateTimeField(verbose_name="수정일" , auto_now=True)

class MettingCommentReply(models.Model):
    user = models.ForeignKey(User, verbose_name="작성자", on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, verbose_name="미팅", on_delete=models.CASCADE)
    comment = models.ForeignKey(MeetingComment, verbose_name="댓글", on_delete=models.CASCADE, related_name="reply")
    content = models.TextField(verbose_name="대댓글내용")
    created_at = models.DateTimeField(verbose_name="작성일" , auto_now_add=True,)
    updated_at = models.DateTimeField(verbose_name="수정일" , auto_now=True)