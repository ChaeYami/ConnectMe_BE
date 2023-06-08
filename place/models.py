from django.db import models
from user.models import User


class Place(models.Model):
    # verbose name지정
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='place_user')
    title = models.CharField(max_length=50)
    # 장소에서 이미지 여러개
    image = models.ImageField(blank=True, null=True)
    content = models.TextField()
    bookmark = models.ManyToManyField(User, related_name='place_bookmark')
    # 좋아요 추가하기
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PlaceComment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='place_comment_user')
    place = models.ForeignKey(
        Place, on_delete=models.CASCADE, related_name='place_comment_place')
    content = models.TextField()
    # 대댓글 구현
    main_comment = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
