from django.db import models
from user.models import User


class Counsel(models.Model):
    user = models.ForeignKey(User, verbose_name="작성자", on_delete=models.CASCADE)
    title = models.CharField(max_length=50, verbose_name="제목")
    content = models.TextField()
    bookmark = models.ManyToManyField(User, related_name='counsel_bookmark', verbose_name="북마크")
    like = models.ManyToManyField(User, related_name='counsel_like', verbose_name="좋아요")
    created_at = models.DateTimeField(verbose_name="작성일" , auto_now_add=True,)
    updated_at = models.DateTimeField(verbose_name="수정일" , auto_now=True)

    
class CounselComment(models.Model):
    user = models.ForeignKey(User, verbose_name="댓글작성자", on_delete=models.CASCADE, related_name="counsel_comment_user")
    counsel= models.ForeignKey(Counsel, on_delete=models.CASCADE, related_name="counsel_comment_counsel")
    content = models.TextField()
    like = models.ManyToManyField(User, related_name='counsel_comment_like', verbose_name="좋아요")
    created_at = models.DateTimeField(verbose_name="작성일" , auto_now_add=True,)
    updated_at = models.DateTimeField(verbose_name="수정일" , auto_now=True)
    
class CounselReply(models.Model):
    user = models.ForeignKey(User, verbose_name="댓글작성자", on_delete=models.CASCADE, related_name="counsel_reply_user")
    counsel= models.ForeignKey(Counsel, on_delete=models.CASCADE)
    comment = models.ForeignKey(CounselComment, verbose_name="댓글", on_delete=models.CASCADE, related_name="reply")
    content = models.TextField()
    like = models.ManyToManyField(User, related_name='counsel_reply_like', verbose_name="좋아요")
    created_at = models.DateTimeField(verbose_name="작성일" , auto_now_add=True,)
    updated_at = models.DateTimeField(verbose_name="수정일" , auto_now=True)

