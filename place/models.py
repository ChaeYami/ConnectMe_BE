from django.db import models
from user.models import User


class Place(models.Model):
    CHOICES = [
        ('밥','밥'),
        ('술','술'),
        ('카페','카페'),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='place_user', verbose_name='작성자')
    title = models.CharField(max_length=50, verbose_name='제목')
    content = models.TextField(verbose_name='내용')
    category = models.CharField(max_length=20, verbose_name='카테고리', choices=CHOICES)
    sort = models.CharField(max_length=20, verbose_name='구분')
    address = models.CharField(max_length=255, verbose_name='주소')
    score = models.FloatField(verbose_name='별점')
    price = models.CharField(max_length=255, verbose_name='가격')
    hour = models.CharField(max_length=255, verbose_name='영업시간')
    holiday = models.CharField(max_length=255, verbose_name='휴일')
    bookmark = models.ManyToManyField(
        User, related_name='place_bookmark', verbose_name='북마크')
    like = models.ManyToManyField(
        User, related_name='place_like', verbose_name='좋아요')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성날짜')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정날짜')

class PlaceImage(models.Model):
    image = models.ImageField(blank=True, null=True, verbose_name='이미지', upload_to="%Y/%m/%d")
    place = models.ForeignKey(Place, on_delete=models.CASCADE, verbose_name='게시글', related_name='place_image_place')

class PlaceComment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='place_comment_user', verbose_name='댓글작성자')
    place = models.ForeignKey(
        Place, on_delete=models.CASCADE, related_name='place_comment_place', verbose_name='게시글')
    content = models.TextField(verbose_name='내용', null=True)
    # 대댓글
    main_comment = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, verbose_name='상위댓글', related_name='reply')
    deep = models.PositiveBigIntegerField(null=True, default=0, verbose_name='댓글단계')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성날짜')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정날짜')
