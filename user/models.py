from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator

from django.utils import timezone

import os
import base64
import hashlib
import hmac
import time
import requests

from decouple import config

from random import randint

# from my_settings import (
#     NAVER_ACCESS_KEY_ID,
#     NAVER_SMS_SECRET_KEY,
#     SERVICE_ID
# )


''' 유저 모델 시작 '''

class UserManager(BaseUserManager):
    def create_user(self, account, email, phone, password=None, **extra_fields):
        if not account:
            raise ValueError("아이디를 입력해주세요.")
        if not email:
            raise ValueError("이메일을 입력해주세요.")
        if not phone:
            raise ValueError("휴대폰 번호를 입력해주세요.")

        user = self.model(
            account=account,
            email=self.normalize_email(email),
            phone=phone,
            **extra_fields,
        )
        user.set_password(password)

        user.save(using=self._db)
        return user

    # admin
    def create_superuser(self, account, password=None, **extra_fields):
        user = self.create_user(account=account, password=password, **extra_fields)

        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        Profile.objects.create(user=user)
        return user

    # staff
    def create_staffuser(self, account, password=None, **extra_fields):
        user = self.create_user(account=account, password=password, **extra_fields)

        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        Profile.objects.create(user=user)
        return user


# 유저모델
class User(AbstractBaseUser):
    class Meta:
        db_table = "User"

    account = models.CharField("아이디", max_length=20, unique=True)
    email = models.EmailField("이메일", max_length=255, unique=True)
    phone = models.CharField(
        "전화번호", max_length=11
    )  # 작동 확인을 위해 임시로 , unique = True 제외함 꼭 추가할 것
    nickname = models.CharField("닉네임", max_length=15)
    joined_at = models.DateTimeField("가입일", auto_now_add=True)
    warning = models.IntegerField("신고횟수", default=0)
    is_blocked = models.BooleanField("차단여부", default=False)
    is_certify = models.BooleanField("번호인증여부", default=False)

    SIGNUP_TYPES = [
        ("일반", "일반"),
        ("카카오", "카카오"),
        ("구글", "구글"),
        ("네이버", "네이버"),
    ]
    signup_type = models.CharField(
        "로그인유형", max_length=10, choices=SIGNUP_TYPES, default="일반"
    )

    is_active = models.BooleanField("활성화", default=False)  # 이메일 인증 전에는 비활성화
    is_staff = models.BooleanField("스태프", default=False)
    is_admin = models.BooleanField("관리자", default=False)

    friends = models.ManyToManyField(
        "self", related_name="friends", blank=True
    )  # user_friends : 친구 상태 테이블

    objects = UserManager()

    USERNAME_FIELD = "account"
    REQUIRED_FIELDS = [
        "email",
        "phone",
    ]

    def __str__(self):
        return self.account

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


''' 유저 모델 끝 '''


"""
user_friend : 친구신청 상태 테이블
user_friends : 친구 상태 테이블
"""


class Friend(models.Model):
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_friend_requests"
    )
    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_friend_requests"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "신청중"), ("accepted", "수락됨"), ("rejected", "거절됨")],
        default="신청중",
    )


''' 프로필 시작 '''

class Profile(models.Model):
    profile_img = models.ImageField(
        "프로필사진", null=True, blank=True, default=None, upload_to="profile_img/"
    )
    prefer_region = models.CharField("선호지역", max_length=10, default="전국", blank=True)
    current_region1 = models.CharField("현재 행정시", max_length=50, blank=True, null=True)
    current_region2 = models.CharField("현재 행정구", max_length=50, blank=True, null=True)
    # 자바스크립트에서 도/특별시/광역시를 고르면 해당하는 시/군/구를 고르게 한 다음 해당 시/군/구만 텍스트로 보내올 예정 (탁근님이 할 거임 쿠다사이)

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name="회원", related_name="user_profile"
    )

    MBTI = [
        ("ALL", "ALL"),
        ("ENFJ", "ENFJ"),
        ("ENFP", "ENFP"),
        ("ENTJ", "ENTJ"),
        ("ENTP", "ENTP"),
        ("ESFJ", "ESFJ"),
        ("ESFP", "ESFP"),
        ("ESTJ", "ESTJ"),
        ("ESTP", "ESTP"),
        ("INFJ", "INFJ"),
        ("INFP", "INFP"),
        ("INTJ", "INTJ"),
        ("INTP", "INTP"),
        ("ISFJ", "ISFJ"),
        ("ISFP", "ISFP"),
        ("ISTJ", "ISTJ"),
        ("ISTP", "ISTP"),
    ]
    mbti = models.CharField(
        "MBTI", choices=MBTI, max_length=4, blank=True, null=True, default="ALL"
    )
    age = models.IntegerField("나이", default="0", blank=True, null=True)
    age_range = models.CharField(
        "나잇대", max_length=20, blank=True, null=True, default="ALL"
    )
    introduce = models.CharField(
        "자기소개", max_length=225, blank=True, null=True, default=""
    )

    def __str__(self):
        return self.user.account, self.user.nickname


class ProfileAlbum(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="회원", related_name="user_album"
    )
    album_img = models.ImageField(
        blank=True, null=True, verbose_name="이미지", upload_to="album_%Y/%m/%d"
    )


''' 프로필 끝 '''


''' sms 인증 모델 '''

# 회원가입 sms 인증번호 발송
class CertifyPhoneSignup(models.Model):
    phone = models.CharField("전화번호", max_length=11)
    auth_number = models.IntegerField(
        "인증 번호", default=0, validators=[MaxValueValidator(9999)]
    )
    expired_at = models.DateTimeField("만료")
    is_certify = models.BooleanField("인증여부", default=False)

    def save(self, *args, **kwargs):
        self.auth_number = randint(1000, 10000)
        self.expired_at = timezone.now() + timezone.timedelta(minutes=5)
        super().save(*args, **kwargs)
        # self.send_sms()

    def send_sms(self):
        timestamp = str(int(time.time() * 1000))
        access_key = config("NAVER_ACCESS_KEY_ID")
        secret_key = bytes(config("NAVER_SMS_SECRET_KEY"), "UTF-8")
        service_id = config("SERVICE_ID")
        method = "POST"
        uri = f"/sms/v2/services/{service_id}/messages"
        message = method + " " + uri + "\n" + timestamp + "\n" + access_key
        message = bytes(message, "UTF-8")
        signing_key = base64.b64encode(
            hmac.new(secret_key, message, digestmod=hashlib.sha256).digest()
        )

        url = f"https://sens.apigw.ntruss.com/sms/v2/services/{service_id}/messages"

        data = {
            "type": "SMS",
            "from": f'{config("FROM_PHONE_NUMBER")}',
            "content": f"[Connect ME] 인증 번호 : [{self.auth_number}]\n인증번호를 입력해주세요. (제한시간:5분)",
            "messages": [{"to": f"{self.phone}"}],
        }

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "x-ncp-apigw-timestamp": timestamp,
            "x-ncp-iam-access-key": access_key,
            "x-ncp-apigw-signature-v2": signing_key,
        }

        requests.post(url, json=data, headers=headers)

    def __str__(self):
        return f"[휴대폰 번호]{self.phone}"


# 아이디찾기 sms 인증번호 발송
class CertifyPhoneAccount(models.Model):
    auth_number = models.IntegerField(
        "인증 번호", default=0, validators=[MaxValueValidator(9999)]
    )
    expired_at = models.DateTimeField("만료")

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="회원")

    def save(self, *args, **kwargs):
        self.auth_number = randint(1000, 10000)
        self.expired_at = timezone.now() + timezone.timedelta(minutes=5)
        super().save(*args, **kwargs)
        self.send_sms()

    def send_sms(self):
        timestamp = str(int(time.time() * 1000))
        access_key = config("NAVER_ACCESS_KEY_ID")
        secret_key = bytes(config("NAVER_SMS_SECRET_KEY"), "UTF-8")
        service_id = config("SERVICE_ID")
        method = "POST"
        uri = f"/sms/v2/services/{service_id}/messages"
        message = method + " " + uri + "\n" + timestamp + "\n" + access_key
        message = bytes(message, "UTF-8")
        signing_key = base64.b64encode(
            hmac.new(secret_key, message, digestmod=hashlib.sha256).digest()
        )

        url = f"https://sens.apigw.ntruss.com/sms/v2/services/{service_id}/messages"

        data = {
            "type": "SMS",
            "from": f'{config("FROM_PHONE_NUMBER")}',
            "content": f"[Connect ME] 인증 번호 : [{self.auth_number}]\n인증번호를 입력해주세요. (제한시간:5분)",
            "messages": [{"to": f"{self.user.phone}"}],
        }

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "x-ncp-apigw-timestamp": timestamp,
            "x-ncp-iam-access-key": access_key,
            "x-ncp-apigw-signature-v2": signing_key,
        }

        requests.post(url, json=data, headers=headers)

    def __str__(self):
        return f"[휴대폰 번호]{self.user.phone}"

''' 신고/차단 모델 시작 '''
# 신고목록
class Report(models.Model):
    report_user = models.ForeignKey(
        User, related_name="report_user", verbose_name="신고자", on_delete=models.CASCADE
    )
    reported_user = models.ForeignKey(
        User,
        related_name="reported_user",
        verbose_name="피신고자",
        on_delete=models.CASCADE,
    )
    reported_at = models.DateTimeField(verbose_name="신고시각", auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["report_user", "reported_user"], name="no_duplication"
            )
        ]

# 차단목록
class Blacklist(models.Model):
    blocked_user = models.ForeignKey(
        User, verbose_name="차단된 유저", on_delete=models.CASCADE
    )
    blocked_at = models.DateTimeField(verbose_name="차단 시간", auto_now_add=True)
    blocked_count = models.PositiveSmallIntegerField(verbose_name="차단 횟수", default=1)
