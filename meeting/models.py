from django.db import models

from user.models import User
# Create your models here.

'''모임 글 모델 시작'''
class Meeting(models.Model):
    user = models.ForeignKey(User, verbose_name="작성자", on_delete=models.CASCADE, related_name="my_meeting")
    title = models.CharField(verbose_name="제목", max_length=50)
    content = models.TextField(verbose_name="모임내용",)
    created_at = models.DateTimeField(verbose_name="작성일" , auto_now_add=True,)
    updated_at = models.DateTimeField(verbose_name="수정일" , auto_now=True)
    bookmark = models.ManyToManyField(User, verbose_name="북마크", blank=True, related_name="bookmark_meeting")
    join_meeting = models.ManyToManyField(User, verbose_name="참가하기", blank=True, related_name="join_meeting")
    meeting_city = models.CharField(verbose_name="지역", max_length=10)
    meeting_at = models.TextField(verbose_name="모임일")
    num_person_meeting = models.TextField(verbose_name="인원수",)
    meeting_status = models.CharField(verbose_name="모집상태", max_length=10, default="모집중")
    place_title = models.TextField(verbose_name="모임장소")
    place_address = models.TextField(verbose_name="모임주소")

'''모임 글 모델 끝'''

'''모임 댓글 시작'''
class MeetingComment(models.Model):
    user = models.ForeignKey(User, verbose_name="댓글작성자", on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, verbose_name="미팅", on_delete=models.CASCADE, related_name="comment") #Nested Serializer 사용을 위해 related_name 지정
    content = models.TextField(verbose_name="댓글내용")
    created_at = models.DateTimeField(verbose_name="작성일" , auto_now_add=True,)
    updated_at = models.DateTimeField(verbose_name="수정일" , auto_now=True)
'''모임 댓글 모델 끝'''

'''모임 대댓글 모델 시작'''
class MeetingCommentReply(models.Model):
    user = models.ForeignKey(User, verbose_name="대댓글작성자", on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, verbose_name="미팅", on_delete=models.CASCADE)
    comment = models.ForeignKey(MeetingComment, verbose_name="댓글", on_delete=models.CASCADE, related_name="reply") #Nested Serializer 사용을 위해 related_name 지정
    content = models.TextField(verbose_name="대댓글내용")
    created_at = models.DateTimeField(verbose_name="작성일" , auto_now_add=True,)
    updated_at = models.DateTimeField(verbose_name="수정일" , auto_now=True)
'''모임 대댓글 모델 끝'''

'''모임 다중 이미지 시작'''
class MeetingImage(models.Model):
    meeting = models.ForeignKey(Meeting, verbose_name="미팅", on_delete=models.CASCADE, related_name="meeting_image")
    image = models.ImageField(blank=True, null=True, verbose_name='이미지', upload_to="meeting_%Y/%m/%d")
'''모임 다중 이미지 끝'''
