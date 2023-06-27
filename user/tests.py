from base64 import urlsafe_b64encode
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from datetime import datetime, timedelta
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.test import TestCase
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from unittest.mock import patch
from user.models import *
from django.test.client import MULTIPART_CONTENT, encode_multipart, BOUNDARY
from PIL import Image
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker
from .serializers import *
import types


class BaseTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
                "account": "basicuser",
                "email": "basicuser@test.com",
                "password": "test1234!!",
                "phone": "01012345670",
                "nickname":"baseuser",
            }
        cls.user = User.objects.create_user(**cls.user_data)
        cls.user_data2 = {
                "account": "basicuser2",
                "email": "basicuser2@test.com",
                "password": "test4321!!",
                "phone": "01012347770",
                "nickname":"cuser2",
                "is_active":True,
        }
        cls.user_data3 = {
                "account": "basicuser3",
                "email": "basicuser3@test.com",
                "password": "test432!!",
                "phone": "01012347870",
                "nickname":"cuser3",
                "is_active":True,
        }
        cls.user3 = User.objects.create_user(**cls.user_data3)
        
class SignupViewTest(BaseTestCase):
    '''
    회원가입
    
    -회원가입시 휴대폰번호 인증이 필요합니다.
    '''
    def test_signup(self):
        '''
        휴대폰 인증번호 발송
        '''
        phone_data = self.user_data2["phone"]
        response = self.client.post(
            path=reverse("certify_phone_signup_view"),
            data={"phone": phone_data},
        )
        auth_data = response.data['auth_number']
        self.assertEqual(response.status_code, 200)
        
        '''
        인증번호 인증
        '''
        response = self.client.post(
            path=reverse("confirm_phone_signup_view"),
            data={"phone": phone_data, "auth_number": auth_data},
        )
        self.assertEqual(response.status_code, 200)
        '''
        회원가입 완료
        '''
        response = self.client.post(
            path=reverse("user_view"),
            data=self.user_data2
            )
        self.assertEqual(response.status_code, 201)
        
        user_data = response.data["user"]
        user = get_user_model().objects.get(id=user_data["id"])

    
    def test_get_user_inform(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("user_view"))
        self.assertEqual(response.status_code, 200)
        
    
#     def test_edit_user_inform(self):
#         '''
#         로그인
#         '''
#         response = self.client.post(
#             path=reverse("login_view"),
#             data=self.user_data3,
#         )
#         self.assertEqual(response.status_code, 200)
#         access_token = response.data['access']
        
#         certify_phone_signup = CertifyPhoneSignup.objects.create(
#             phone=self.user_data3["phone"],
#             auth_number=1234,
#             expired_at=datetime.now() + timedelta(minutes=10),
#             is_certify=True
#         )
        
#         print(certify_phone_signup)
        
        
#         '''
#         유저 정보 수정
#         '''
#         self.client.force_authenticate(user=self.user3)
#         updated_data = {
#             "phone": "09876543210",
#         }
#         response = self.client.patch(
#             path=reverse("user_view"),
#             HTTP_AUTHORIZATION = f"Bearer {access_token}",
#             data=updated_data,
#         )
#         print(response.data)
        
#         self.assertEqual(response.status_code, 200)
        
        
        
class VerifyEmailViewTest(BaseTestCase):
        '''
        이메일 인증
        '''
        def test_verify_email(self):
            
            # 이메일 인증 URL 생성
            uidb64 = urlsafe_base64_encode(force_bytes(self.user.id))
            token = default_token_generator.make_token(self.user)
            email_verification_url = reverse("verify_email_view", args=[uidb64, token])

            # 이메일 인증 요청
            response = self.client.get(email_verification_url)
            self.assertEqual(response.status_code, 302)
    
    