from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APITestCase

import tempfile
from PIL import Image
from datetime import datetime, timedelta

from user.models import *
from .serializers import *




def get_temporary_image():
    '''
    임의 이미지 생성
    '''
    temp_file = tempfile.NamedTemporaryFile(suffix=".png")
    size = (10, 10)
    color = (255, 0, 0, 0)
    image = Image.new("RGBA", size, color)
    image.save(temp_file, "png")
    temp_file.seek(0)
    return SimpleUploadedFile(temp_file.name, temp_file.read(), content_type="image/png")

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
        cls.user_data4 = {
                "account": "basicuser4",
                "email": "basicuser4@test.com",
                "password": "test432a!!",
                "phone": "01012377870",
                "nickname":"cuser4",
                "is_active":True,
        }
        cls.user4 = User.objects.create_user(**cls.user_data4)
        cls.user_data5 = {
                "account": "basicuser5",
                "email": "basicuse5@test.com",
                "password": "5test123!",
                "phone": "01052345670",
                "nickname":"baseuse5",
            }
        cls.user5 = User.objects.create_user(**cls.user_data5)
        cls.image_data = get_temporary_image()
        cls.image_data2 = get_temporary_image()
        cls.image_data3 = get_temporary_image()
        
        
    def setUp(self):
        self.user3_access_token = self.client.post(reverse("login_view"), self.user_data3).data.get("access")
        self.user4_access_token = self.client.post(reverse("login_view"), self.user_data4).data.get("access")
        
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
        # user_data = response.data["user"]
        # user = get_user_model().objects.get(id=user_data["id"])

    
    def test_get_user_inform(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("user_view"))
        self.assertEqual(response.status_code, 200)
        
    
    def test_edit_user_inform(self):
        certify_phone_signup = CertifyPhoneSignup.objects.create(
            phone="09876543210",
            auth_number=1234,
            expired_at=datetime.now() + timedelta(minutes=10),
            is_certify=True
        )
        
        
        '''
        유저 정보 수정
        '''
        self.client.force_authenticate(user=self.user3)
        updated_data = {
            "phone": "09876543210",
        }
        response = self.client.patch(
            path=reverse("user_view"),
            HTTP_AUTHORIZATION = f"Bearer {self.user3_access_token}",
            data=updated_data,
        )
        self.assertEqual(response.status_code, 200)
       
        
    def test_delete_user_inform(self):
        response = self.client.delete(
            path=reverse("user_view"),
            HTTP_AUTHORIZATION = f"Bearer {self.user3_access_token}",
            data=self.user_data3,
        )
        self.assertEqual(response.status_code, 204)
        
    def test_fail_diffrent_password_delete_user(self):
        user_datas = {
            **self.user_data3,
            "password": "test!!",
        }
        response = self.client.delete(
            path=reverse("user_view"),
            HTTP_AUTHORIZATION = f"Bearer {self.user3_access_token}",
            data=user_datas,
        )
        self.assertEqual(response.status_code, 400)
        
        
class LoginViewTest(BaseTestCase):
    '''
    로그인
    '''
    def test_login_user(self):
        response = self.client.post(
            path=reverse("login_view"),
            data=self.user_data3,
        )
        self.assertEqual(response.status_code, 200)
        

class ChangePasswordView(BaseTestCase):
    '''
    비번 변경 (로그인)
    '''
    def test_change_password(self):
        change_data = {
            **self.user_data3,
            "password":"qlqjsdle2@",
            "repassword":"qlqjsdle2@",
            "confirm_password":"test432!!",
        }
        response = self.client.put(
            path=reverse("password_change_view"),
            HTTP_AUTHORIZATION = f"Bearer {self.user3_access_token}",
            data=change_data,
        )
        self.assertEqual(response.status_code, 200)
        
        
class FriendViewTest(BaseTestCase):
    def test_request_friend(self):
        '''
        친구 신청
        '''
        response = self.client.post(
            path=reverse("friend_request_view", kwargs={"user_id" : self.user4.id}),
            HTTP_AUTHORIZATION = f"Bearer {self.user3_access_token}",
        )
        self.assertEqual(response.status_code, 201)
        
        '''
        친구 신청 목록
        '''
        response = self.client.get(
            path=reverse("received_list"),
            HTTP_AUTHORIZATION = f"Bearer {self.user3_access_token}",
        )
        self.friend_id = response.data[-1]["id"] 
        self.assertEqual(response.status_code, 200)
        
        
    def test_accept_request_friend(self):
        '''
        친구 신청 수락
        '''
        self.test_request_friend()
        response = self.client.post(
            path=reverse("friend_request_accept_view", kwargs={"friend_request_id": self.friend_id}),
            HTTP_AUTHORIZATION = f"Bearer {self.user4_access_token}"
        )
        self.assertEqual(response.status_code, 200)
        
    
    def test_refuse_request_friend(self):
        '''
        친구 신청 삭제
        '''
        self.test_request_friend()
        response = self.client.post(
            path=reverse("friend_request_reject_view", kwargs={"friend_request_id":self.friend_id}),
            HTTP_AUTHORIZATION = f"Bearer {self.user4_access_token}"
        )
        self.assertEqual(response.status_code, 200)

            
    def test_list_friend(self):
        '''
        친구 리스트
        '''
        self.test_accept_request_friend()
        response = self.client.get(
            path=reverse("friends_list"),
            HTTP_AUTHORIZATION = f"Bearer {self.user4_access_token}"
        )
        self.assertEqual(response.status_code, 200)
        
        
    def test_delete_friend(self):
        '''
        친구 삭제
        '''
        self.test_accept_request_friend()
        response = self.client.delete(
            path=reverse("friend-delete", kwargs={"friend_id":self.friend_id}),
            HTTP_AUTHORIZATION = f"Bearer {self.user4_access_token}"
        )
        self.assertEqual(response.status_code, 200)
        
    
class FindUserAccountTest(BaseTestCase):
    def test_send_sms_to_user_for_find_account(self):
        '''
        아이디 찾기 (sms 발송)
        '''
        self.client.force_authenticate(user=self.user3)
        response = self.client.post(
            path=reverse("certify_phone_account_view"),
            HTTP_AUTHORIZATION = f"Bearer {self.user3_access_token}",
            data=self.user_data3,
        )
        self.auth_num = response.data["auth_number"]
        self.assertEqual(response.status_code, 200)
        
        
    def test_confirm_sending_sms_to_user_for_find_account(self):
        '''
        sms 인증하기
        '''
        self.test_send_sms_to_user_for_find_account()
        user_datas = {
            **self.user_data3,
            "auth_number": self.auth_num,
        }
        self.client.force_authenticate(user=self.user3)
        response = self.client.post(
            path=reverse("find_account_view"),
            HTTP_AUTHORIZATION = f"Bearer {self.user3_access_token}",
            data=user_datas,
        )
        self.assertEqual(response.status_code, 200)
        
        
class UserPasswordTest(BaseTestCase):
    def test_send_email_to_user_for_find_password(self):
        '''
        비번찾기 (이메일)
        '''
        self.client.force_authenticate(user=self.user3)
        response = self.client.post(
            path=reverse("password_reset"),
            HTTP_AUTHORIZATION = f"Bearer {self.user3_access_token}",
            data=self.user_data3,
        )
        self.assertEqual(response.status_code, 200)
        
    def test_check_password_token(self):
        '''
        비번 재설정
        '''
        self.test_send_email_to_user_for_find_password()
        # 비밀번호 재설정 이메일을 받은 사용자의 토큰 확인
        
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.id))
        token = default_token_generator.make_token(self.user)
        
        user_datas = {
            "repassword" : "!test432a!",
            "password" : "!test432a!",
            "token" : token,
            "uidb64" : uidb64,
        }
        
        response = self.client.put(
            path=reverse("password_reset_confirm"),
            HTTP_AUTHORIZATION = f"Bearer {self.user3_access_token}",
            data=user_datas,
        )
        self.assertEqual(response.status_code, 200)


class ProfileViewTest(BaseTestCase):
    def test_get_profile(self):
        '''
        프로필 보기
        '''
        Profile.objects.create(
            user = self.user3,
            id=self.user3.id
        )
        
        response = self.client.get(
            path=reverse("profile_view", kwargs={"user_id":self.user3.id}),
            HTTP_AUTHORIZATION = f"Bearer {self.user3_access_token}",
        )
        self.user_profile = response.data
        self.assertEqual(response.status_code, 200)
        
        
    def test_edit_profile(self):
        '''
        프로필 보기
        '''
        self.test_get_profile()
        edit_profile = {
            **self.user_profile,
            "account": "edit user",
            "nickname": "edit nickname",
            "profile_img": self.image_data,
            "prefer_region": "경기도 수원시",
            "mbti": "INFP",
            "age": 28,
            "introduce": "edit introduce",
        }
        
        response = self.client.patch(
            path=reverse("profile_view", kwargs={"user_id":self.user3.id}),
            HTTP_AUTHORIZATION = f"Bearer {self.user3_access_token}",
            data=edit_profile,
        )
        self.assertEqual(response.status_code, 200)
        
        
class ProfileAlbumViewTest(BaseTestCase):       
    def test_add_profile_album(self):
        '''
        프로필 앨범 추가
        '''
        album_img_list = [
            ("album_img", [self.image_data, self.image_data2, self.image_data3]),
        ]
        response = self.client.post(
            path=reverse("profile_album_view", kwargs={"user_id":self.user3.id}),
            HTTP_AUTHORIZATION = f"Bearer {self.user3_access_token}",
            data=dict(album_img_list),
            format="multipart",
        )
        self.assertEqual(response.status_code, 200)
        
        
    def test_get_profile_album(self):
        '''
        프로필 앨범 보기
        '''
        self.test_add_profile_album()
        response = self.client.get(
            path=reverse("profile_album_view", kwargs={"user_id":self.user3.id}),
            HTTP_AUTHORIZATION = f"Bearer {self.user3_access_token}"
        )
        self.album = response.data
        self.assertEqual(response.status_code, 200)
        
        
    def test_delete_profile_album(self):
        '''
        프로필 사진 삭제
        '''
        self.test_get_profile_album()
        image_id = self.album[0]['id']
        response = self.client.delete(
            path=reverse("profile_album_delete_view", kwargs={"user_id":self.user3.id, "image_id":image_id}),
            HTTP_AUTHORIZATION = f"Bearer {self.user3_access_token}"
        )
        self.assertEqual(response.status_code, 200)
        
        
class ReportUserViewTest(BaseTestCase):
    def test_report_user(self):
        '''
        (비매너)유저 신고하기
        '''
        response = self.client.post(
            path=reverse("report_view", kwargs={"user_id":self.user4.id}),
            HTTP_AUTHORIZATION = f"Bearer {self.user3_access_token}"
        )
        self.assertEqual(response.status_code, 200)
        
class CurrentRegionViewTest(BaseTestCase):
    def test_user_current_region(self):
        '''
        유저의 현재지역 저장
        '''
        Profile.objects.create(
            user = self.user3,
            id=self.user3.id
        )
        
        user_datas = {
            "user": self.user3.id,
            "current_region1" : "고양이시",
            "current_region2" : "고양이동",
        }
        
        response = self.client.patch(
            path=reverse("region_view"),
            HTTP_AUTHORIZATION = f"Bearer {self.user3_access_token}",
            data=user_datas
        )
        self.assertEqual(response.status_code, 200)
        
        
class VerifyEmailViewTest(BaseTestCase):
        '''
        이메일 인증
        '''
        def test_verify_email(self):
            # 이메일 인증 URL 생성
            uidb64 = urlsafe_base64_encode(force_bytes(self.user5.id))
            token = default_token_generator.make_token(self.user5)
            
            InactiveUser.objects.create(
                inactive_user=self.user5
            )

            # 이메일 인증 요청
            response = self.client.get(
                path=reverse("verify_email_view", kwargs={"uidb64":uidb64, "token":token})
            )
            self.assertEqual(response.status_code, 302)
    