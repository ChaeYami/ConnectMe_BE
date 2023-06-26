from django.test import TestCase

from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status

from user.models import User, Profile
from counsel.models import (
    Counsel,
    CounselComment,
    CounselReply,
)

class CounselViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.account ='test1account'
        cls.email='test1@naver.com'
        cls.phone='01012345678'
        cls.password='test1234!!'
        cls.user_data = {"account":"test1account","password" :"test1234!!"}
        cls.user = User.objects.create_user(account=cls.account, email=cls.email, phone=cls.phone, password=cls.password)
        Profile.objects.create(user=cls.user)
        
        # cls.counsel_data = {"title":"test title", "content":"test content"}
        # cls.counsel = Counsel.objects.create(**cls.counsel_data, user = cls.user)
        
        cls.user.is_active = True
        cls.user.save()
        
    def setUp(self):
        self.access_token = self.client.post(reverse("user:login_view"), self.user_data).data["access"]

    # 전체 게시글 조회
    def test_all_counsel_list(self):
        response = self.client.get(
            path=reverse("counsel_view"), 
            HTTP_AUTHORIZATION = f"Bearer{self.access_token}",
        )
        self.assertEqual(response.status_code, 200)
        
        
class CounselDetailViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.account ='test1account'
        cls.email='test1@naver.com'
        cls.phone='01012345678'
        cls.password='test1234!!'
        cls.user_data = {"account":"test1account","password" :"test1234!!"}
        cls.user = User.objects.create_user(account=cls.account, email=cls.email, phone=cls.phone, password=cls.password)
        Profile.objects.create(user=cls.user)
        
        cls.counsel_data = {"title":"test title", "content":"test content"}
        # cls.counsel = Counsel.objects.create(**cls.counsel_data, user = cls.user)
        
        cls.user.is_active = True
        cls.user.save()
    
    def setUp(self):
        self.access_token = self.client.post(reverse("user:login_view"), self.user_data).data["access"]
        
    ''' 로그인 테스트 '''
    def test_login(self):
        url = reverse("user:login_view")
        data = {
            'account': self.account,
            'password': self.password
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # 로그인 요청이 성공적으로 처리되었는지 확인
        
        
    # 게시글 작성 성공
    def test_counsel_create(self):
        response = self.client.post(
            path=reverse("counsel_view"), 
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}", 
            data=self.counsel_data, 
            )
        
        self.assertEqual(response.status_code, 200)
        
    # 게시글 작성 실패 - 비로그인
    def test_fail_if_not_logged_in_counsel_post(self):
        response = self.client.post(
            path=reverse("counsel_view"), 
            data=self.counsel_data, 
            )
        self.assertEqual(response.status_code, 401) # Unauthorized
        
    # 게시글 작성 실패 - 제목없음
    def test_counsel_create_no_title(self):
        response = self.client.post(
            path=reverse("counsel_view"), 
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}", 
            data={"title" : "", "content" : "test content"}, 
            )
        self.assertEqual(response.status_code, 400) # serializer is_valid = False
    
    # 게시글 작성 실패 - 내용없음
    def test_counsel_create_no_content(self):
        response = self.client.post(
            path=reverse("counsel_view"), 
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}", 
            data={"title" : "test title", "content" : ""}, 
            )
        self.assertEqual(response.status_code, 400) # serializer is_valid = False
