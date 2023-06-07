from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.exceptions import ValidationError
import os

class UserManager(BaseUserManager):
    def create_user(self, account, email, phone, password = None, **extra_fields):
        if not account:
            raise ValueError("아이디를 입력해주세요.")
        if not email:
            raise ValueError("이메일을 입력해주세요.")
        if not phone:
            raise ValueError("휴대폰 번호를 입력해주세요.")
        
        user = self.model(account=account, email=self.normalize_email(email), phone = phone, **extra_fields)
        user.set_password(password)
        
        user.save(using=self._db)
        return user
    
    def create_superuser(self, account, email, phone, password = None, **extra_fields):
        user = self.create_user(account = account, email=email, phone = phone, password=password, **extra_fields)

        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user
    
    
# =============== 유저 모델 시작 =============== 
class User(AbstractBaseUser):
    class Meta:
        db_table = "User"
        
    account = models.CharField("아이디", max_length=20, unique=True)
    email = models.EmailField("이메일", max_length=255, unique=True)
    phone = models.CharField("전화번호", max_length=11, blank=True)
    nickname = models.CharField("닉네임", max_length=15)
    joined_at = models.DateTimeField("가입일", auto_now_add=True)
    warning = models.IntegerField("신고횟수", default=0)
    is_blocked = models.BooleanField("차단여부", default=False)
    
    is_staff = models.BooleanField("스태프", default=False)
    is_admin = models.BooleanField("관리자", default=False)
    is_active = models.BooleanField("활성화", default=True) 
    
    objects = UserManager()
    
    USERNAME_FIELD = "account"
    REQUIRED_FIELDS = ["email", "phone",]
    
    def __str__(self):
        return self.account
    
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
    
    @property
    def is_staff(self):
        return self.is_admin
    
# =============== 유저 모델 끝 =============== 
    
    
# =============== 프로필 시작 =============== 

class Profile(models.Model):
    profile_img = models.ImageField("프로필사진", null=True, blank=True, default=None, upload_to="profile_img/")
    region = models.CharField("지역", max_length=10)
    mbti_choices = [
        ('ENFJ','ENFJ'),
        ('ENFP','ENFP'),
        ('ENTJ','ENTJ'),
        ('ENTP','ENTP'),
        ('ESFJ','ESFJ'),
        ('ESFP','ESFP'),
        ('ESTJ','ESTJ'),
        ('ESTP','ESTP'),
        ('INFJ','INFJ'),
        ('INFP','INFP'),
        ('INTJ','INTJ'),
        ('INTP','INTP'),
        ('ISFJ','ISFJ'),
        ('ISFP','ISFP'),
        ('ISTJ','ISTJ'),
        ('ISTP','ISTP'),
    ]
    mbti = models.CharField("MBTI", choices=mbti_choices, max_length=4, blank=True, null=True)
    age = models.IntegerField("나이", default = 0, blank=True, null= True)
    introduce = models.CharField("자기소개", max_length=225, default=None, blank=True, null= True)
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="회원", related_name="user_profile")
    
    def __str__(self):
        return self.user.account, self.user.nickname