from base64 import urlsafe_b64decode, urlsafe_b64encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import DjangoUnicodeDecodeError, force_str, force_bytes
from django.shortcuts import redirect
from django.core.mail import EmailMessage
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from user.serializers import (
    ChangePasswordSerializer,
    RequestListSerializer,
    FriendSerializer,
    ProfileAlbumSerializer,
    SignupSerializer,
    CustomTokenObtainPairSerializer,
    UserDelSerializer,
    ProfileSerializer,
    PasswordResetSerializer,
    SetNewPasswordSerializer,
    EmailThread,
    UserUpdateSerializer,
    ProfileRegionSerializer,
    ActivateAccount,
    UserNickUpdateSerializer
)

from decouple import config

from .models import (
    CertifyPhoneAccount,
    CertifyPhoneSignup,
    Friend,
    ProfileAlbum,
    Report,
    User,
    Profile,
    Blacklist,
    InactiveUser
)
from .validators import phone_validator

import requests
import uuid


""" 회원가입, 회원정보 시작 """

class Util:
    @staticmethod
    def send_email(message):
        email = EmailMessage(
            subject=message["email_subject"],
            body=message["email_body"],
            to=[message["to_email"]],
        )
        EmailThread(email).start()


''' 회원가입, 개인정보 view '''
class UserView(APIView):
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.request.method == "PATCH" or self.request.method == "DELETE":
            return [
                IsAuthenticated(),
            ]
        else:
            return super(UserView, self).get_permissions()

    '''개인정보 보기'''
    def get(self, request):  # /user/
        user = get_object_or_404(User, id=request.user.id)
        serializer = SignupSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    '''회원가입'''
    def post(self, request):  # /user/
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # 토큰 생성
            _uid = urlsafe_b64encode(force_bytes(user.pk))
            uid = str(_uid)[2:-1]
            token = PasswordResetTokenGenerator().make_token(user)

            # 이메일 전송
            email = user.email
            BACKENDBASEURL = config("BACKEND_BASE_URL")
            authurl = f"{BACKENDBASEURL}/user/verify-email/{uid}/{token}/"
            email_body = (
                f"{user.nickname}님 안녕하세요! \n아래 링크를 클릭해 회원가입을 완료해주세요. \n{authurl}"
            )
            message = {
                "email_body": email_body,
                "to_email": email,
                "email_subject": "이메일 인증",
            }
            Util.send_email(message)

            return Response({"message": "가입완료!"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    '''회원정보수정'''
    def patch(self, request):  # /user/
        user = get_object_or_404(User, id=request.user.id)
        serializer = UserUpdateSerializer(
            user, data=request.data, context={"request": request}, partial=True
        )
        if user.signup_type == "일반":
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "수정완료!"}, status=status.HTTP_200_OK)

            else:
                return Response(
                    {"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"message": "소셜로그인 가입자입니다."}, status=status.HTTP_400_BAD_REQUEST
            )

    '''회원 탈퇴 (비활성화, 비밀번호 받아서)'''
    def delete(self, request):  # /user/
        user = get_object_or_404(User, id=request.user.id)
        datas = request.data.copy()
        datas["is_active"] = False
        serializer = UserDelSerializer(user, data=datas)
        if user.check_password(request.data.get("password")):
            if serializer.is_valid():
                serializer.save()
                # 비활성화 테이블
                InactiveUser.objects.create(inactive_user=user)
                
                return Response(
                    {"message": "계정 비활성화 완료"}, status=status.HTTP_204_NO_CONTENT
                )

        else:
            return Response(
                {"message": f"패스워드가 다릅니다"}, status=status.HTTP_400_BAD_REQUEST
            )


''' 회원가입 sms 인증 '''

# 인증번호 발송
class CertifyPhoneSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            phone = request.data["phone"]
            if not phone_validator(phone):
                # 인증모델 생성로직
                # CertifyPhoneSignup.objects.create(phone=phone)
                signup = CertifyPhoneSignup(phone=phone)
                signup.save()
                signup.send_sms()

                return Response(
                    {"message": "인증번호가 발송되었습니다. 확인부탁드립니다.", "auth_number": signup.auth_number}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"message": "휴대폰 번호를 확인해주세요"}, status=status.HTTP_400_BAD_REQUEST
                )

        except:
            return Response(
                {"message": "휴대폰 번호를 입력해주세요"}, status=status.HTTP_400_BAD_REQUEST
            )


# 인증번호 확인
class ConfirmPhoneSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            phone = request.data["phone"]
            auth_number = request.data["auth_number"]

            confirm_phone = CertifyPhoneSignup.objects.filter(phone=phone).last()

            if confirm_phone.expired_at < timezone.now():
                return Response(
                    {"message": "인증 번호 시간이 지났습니다."}, status=status.HTTP_400_BAD_REQUEST
                )

            if confirm_phone.auth_number != int(auth_number):
                return Response(
                    {"message": "인증 번호가 틀립니다. 다시 입력해주세요"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            confirm_phone.is_certify = True
            confirm_phone.save()

            return Response({"message": "전화번호 인증이 완료되었습니다."}, status=status.HTTP_200_OK)

        except:
            return Response(
                {"message": "인증번호를 확인해주세요."}, status=status.HTTP_400_BAD_REQUEST
            )


''' 회원가입 이메일 인증 '''
class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        try:
            # URL에 포함된 uid를 디코딩하여 사용자 식별
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        token_generator = PasswordResetTokenGenerator()
        FRONTEND_BASE_URL = config("FRONTEND_BASE_URL")
        # 사용자가 존재하고 토큰이 유효한지 확인
        if user is not None and token_generator.check_token(user, token):
            # 이메일 인증 완료 처리 - 유저 활성화
            user.is_active = True
            user.save()
            InactiveUser.objects.get(inactive_user_id=uid).delete()
            return redirect(f"{FRONTEND_BASE_URL}/confirm_email.html")
        else:
            return redirect("잘못되었거나 만료된 링크 프론트 html")

'''계정 재활성화'''

class ActivateAccountView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ActivateAccount(data=request.data)
        email = serializer.validated_data.get("email")
        if serializer.is_valid:
            try:
                # 유저가 비활성화된 상태인 경우에만 계정을 활성화할 수 있도록 검증
                user = User.objects.get(email=email, is_active=False)
                
                # 토큰 생성
                _uid = urlsafe_b64encode(force_bytes(user.pk))
                uid = str(_uid)[2:-1]
                token = PasswordResetTokenGenerator().make_token(user)
                # 이메일 전송
                BACKENDBASEURL = config("BACKEND_BASE_URL")
                authurl = f"{BACKENDBASEURL}/user/verify-email/{uid}/{token}/"
                email_body = f"계정 재활성화를 위한 이메일 인증 링크입니다. 아래 링크를 클릭해 계정 재활성화를 진행해주세요. \n{authurl}"
                message = {
                    "email_body": email_body,
                    "to_email": email,
                    "email_subject": "계정 재활성화 이메일 인증",
                }
                Util.send_email(message)
                return Response(
                    {"message": "이메일을 통해 계정 재활성화 링크가 전송되었습니다."},
                    status=status.HTTP_200_OK,
                )
            except User.DoesNotExist:
                return Response(
                    {"message": "비활성화된 상태가 아닌 계정입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
            
""" 회원가입, 회원정보 끝 """


''' 로그인 '''
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


''' 비밀번호 변경 '''
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = get_object_or_404(User, id=request.user.id)
        if user.signup_type == "일반":
            serializer = ChangePasswordSerializer(
                user, data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "비밀번호 변경이 완료되었습니다! 다시 로그인해주세요."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "소셜로그인 가입자는 비밀번호 변경을 할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )


""" 프로필 시작 """


''' 친구추천 (작성된 프로필 기반) '''
class ProfileListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, filter_):
        # 지역
        if filter_ == "prefer_region":
            user = get_object_or_404(Profile, user_id=request.user.id)
            prefer_region = user.prefer_region
            admins = User.objects.filter(is_admin=True)  # admin 계정 확인
            admin_ids = [admin.id for admin in admins]
            profiles = Profile.objects.filter(prefer_region=prefer_region).exclude(
                Q(id=request.user.id) | Q(id__in=admin_ids)
            )
            serializer = ProfileSerializer(profiles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # mbti
        elif filter_ == "mbti":
            user = get_object_or_404(Profile, user_id=request.user.id)
            mbti = user.mbti
            admins = User.objects.filter(is_admin=True)  # admin 계정 확인
            admin_ids = [admin.id for admin in admins]
            profiles = Profile.objects.filter(mbti=mbti).exclude(
                Q(id=request.user.id) | Q(id__in=admin_ids)
            )
            serializer = ProfileSerializer(profiles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 나이대
        elif filter_ == "age_range":
            user = get_object_or_404(Profile, user_id=request.user.id)
            age_range = user.age_range
            admins = User.objects.filter(is_admin=True)  # admin 계정 확인
            admin_ids = [admin.id for admin in admins]
            profiles = Profile.objects.filter(age_range=age_range).exclude(
                Q(id=request.user.id) | Q(id__in=admin_ids)
            )
            serializer = ProfileSerializer(profiles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 전체
        elif filter_ == "all":
            user = get_object_or_404(Profile, user_id=request.user.id)
            admins = User.objects.filter(is_admin=True)  # admin 계정 확인
            admin_ids = [admin.id for admin in admins]
            profiles = Profile.objects.all().exclude(
                Q(id=request.user.id) | Q(id__in=admin_ids)
            )
            serializer = ProfileSerializer(profiles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


''' 개인 공개 프로필 '''
class ProfileView(APIView):
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.request.method == "PATCH":
            return [
                IsAuthenticated(),
            ]
        else:
            return super(ProfileView, self).get_permissions()

    # 요청 유저의 정보를 가져올 때 사용할 get_object 인스턴스 정의
    def get_object(self, user_id):
        return get_object_or_404(User, id=user_id)

    # 프로필 보기
    def get(self, request, user_id):
        profile = get_object_or_404(Profile, user=user_id)
        user = get_object_or_404(User, id=user_id)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 프로필 수정
    def patch(self, request, user_id):
        user = self.get_object(user_id)  # 요청 유저의 정보 가져오기

        if user == request.user:
            profile = get_object_or_404(Profile, id=user_id)
            serializer = ProfileSerializer(profile, data=request.data, partial=True)
            user_serizlier = UserNickUpdateSerializer(user, data=request.data, partial=True)
            if serializer.is_valid() and user_serizlier.is_valid():
                serializer.save()
                user_serizlier.save()
                return Response(
                    {"message": "프로필 수정이 완료되었습니다."}, status=status.HTTP_200_OK
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"message": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)


''' 프로필 앨범 '''
class ProfileAlbumView(APIView):
    permission_classes = [IsAuthenticated]

    # 요청 유저의 정보를 가져올 때 사용할 get_object 인스턴스 정의
    def get_object(self, user_id):
        return get_object_or_404(User, id=user_id)

    # 사진첩 보기
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        img = ProfileAlbum.objects.filter(user=user)
        serializer = ProfileAlbumSerializer(img, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 사진 올리기
    def post(self, request, user_id):
        user = get_object_or_404(User, id=request.user.id)
        for data in request.data.getlist("album_img"):
            ProfileAlbum.objects.create(user=user, album_img=data)
        return Response(status.HTTP_200_OK)

# 프로필 앨범 사진 삭제
class ProfileAlbumDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    # 요청 유저의 정보를 가져올 때 사용할 get_object 인스턴스 정의
    def get_object(self, user_id, image_id):
        return get_object_or_404(User, id=user_id)

        # 사진 삭제하기

    def delete(self, request, user_id, image_id):
        user = get_object_or_404(User, id=user_id)
        img = get_object_or_404(ProfileAlbum, id=image_id)

        if request.user == user:
            img.delete()
            return Response(status.HTTP_200_OK)
        else:
            return Response({"message": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)


""" 프로필 끝 """


""" 아이디 찾기 시작 """


''' sms 인증번호 발송 '''
class CertifyPhoneAccountView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            phone = request.data["phone"]
            if not User.objects.filter(phone=phone).exists():
                return Response(
                    {"message": "등록된 휴대폰 번호가 없습니다."}, status=status.HTTP_400_BAD_REQUEST
                )

            else:
                user = User.objects.get(phone=phone)
                user_account = CertifyPhoneAccount.objects.create(user=user)
                user.is_certify = True
                return Response(
                    {"message": "인증번호가 발송되었습니다. 확인부탁드립니다.", "auth_number": user_account.auth_number}, status=status.HTTP_200_OK
                )

        except:
            return Response(
                {"message": "휴대폰 번호를 입력해주세요"}, status=status.HTTP_400_BAD_REQUEST
            )


''' 인증번호 확인 '''
class ConfirmPhoneAccountView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            phone = request.data["phone"]
            auth_number = request.data["auth_number"]

            user = get_object_or_404(User, phone=phone)
            confirm_phone = CertifyPhoneAccount.objects.filter(user=user).last()

            if confirm_phone.expired_at < timezone.now():
                return Response(
                    {"message": "인증 번호 시간이 지났습니다."}, status=status.HTTP_400_BAD_REQUEST
                )

            if confirm_phone.auth_number != int(auth_number):
                return Response(
                    {"message": "인증 번호가 틀립니다. 다시 입력해주세요"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"message": f"회원님의 아이디는 {user.account}입니다."}, status=status.HTTP_200_OK
            )

        except:
            return Response(
                {"message": "인증번호를 확인해주세요."}, status=status.HTTP_400_BAD_REQUEST
            )


""" 아이디 찾기 끝 """


""" 비밀번호 재설정 시작 """

''' 이메일 보내기 '''
class PasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            user = get_object_or_404(User, email=email)
            if user.signup_type == "일반":
                return Response(
                    {"message": "비밀번호 재설정 이메일을 발송했습니다."}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"message": "소셜로그인 가입자는 비밀번호 재설정을 할 수 없습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


''' 비밀번호 재설정 토큰 확인 '''
class PasswordTokenCheckView(APIView):
    def get(self, request, uidb64, token):
        try:
            user_id = force_str(urlsafe_b64decode(uidb64))
            user = get_object_or_404(User, id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {"message": "링크가 유효하지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED
                )

            return Response(
                {"uidb64": uidb64, "token": token}, status=status.HTTP_200_OK
            )

        except DjangoUnicodeDecodeError as identifier:
            return Response(
                {"message": "링크가 유효하지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED
            )


''' 비밀번호 재설정 '''
class SetNewPasswordView(APIView):
    def put(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "비밀번호 재설정 완료"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


''' 비밀번호 재설정 끝 '''


""" 친구맺기 시작 """


''' 친구신청 '''
class FriendView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        from_user = request.user
        to_user = get_object_or_404(User, id=user_id)
        serializer = FriendSerializer(data={"from_user": from_user, "to_user": to_user})
        serializer.is_valid(raise_exception=True)
        friend_request = serializer.save()

        return Response({"message": "친구 신청을 보냈습니다."}, status=status.HTTP_201_CREATED)


''' 친구신청 수락 '''
class FriendAcceptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, friend_request_id):
        friend_request = get_object_or_404(Friend, id=friend_request_id)
        if friend_request.to_user != request.user:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        if friend_request.status != "pending":
            return Response(
                {"message": "이미 처리된 요청입니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        friend_request.status = "accepted"
        friend_request.save()

        from_user = friend_request.from_user
        to_user = friend_request.to_user
        from_user.friends.add(to_user)

        return Response({"message": "친구 신청을 수락했습니다."}, status=status.HTTP_200_OK)


''' 친구신청 거절 '''
class FriendRejectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, friend_request_id):
        friend_request = get_object_or_404(Friend, id=friend_request_id)
        if friend_request.to_user != request.user:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        if friend_request.status != "pending":
            return Response(
                {"message": "이미 처리된 요청입니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        friend_request.delete()

        return Response({"message": "친구 신청을 거절했습니다."}, status=status.HTTP_200_OK)


''' 친구신청목록 '''
class RequestList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = get_object_or_404(User, id=request.user.id)
        list = Friend.objects.filter(
            Q(to_user_id=user.id) | Q(from_user_id=user.id)
        ).exclude(status="accepted")
        serializer = RequestListSerializer(list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


''' 친구목록 '''
class FriendsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = get_object_or_404(User, id=request.user.id)

        friend_requests = Friend.objects.filter(
            Q(from_user=user) | Q(to_user=user), status="accepted"
        )
        serializer = RequestListSerializer(friend_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


''' 친구삭제 '''
class FriendDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, friend_id):
        friend = get_object_or_404(Friend, id=friend_id)

        user1 = User.objects.get(id=friend.from_user_id)
        user2 = User.objects.get(id=friend.to_user_id)
        if friend.from_user != request.user and friend.to_user != request.user:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        # 친구 삭제
        friend.delete()
        user1.friends.remove(user2)

        return Response({"message": "친구를 삭제했습니다."}, status=status.HTTP_200_OK)


""" 친구맺기 끝 """


""" 소셜 로그인 시작 """


''' 카카오로그인 '''
class KakaoLoginView(APIView):
    def get(self, request):
        return Response(config("KAKAO_LOGIN_API_KEY"), status=status.HTTP_200_OK)

    def post(self, request):
        auth_code = request.data.get("code")
        kakao_token_api = "https://kauth.kakao.com/oauth/token"
        FRONTEND_BASE_URL = config("FRONTEND_BASE_URL")
        data = {
            "grant_type": "authorization_code",
            "client_id": config("KAKAO_LOGIN_API_KEY"),
            "redirect_uri": f"{FRONTEND_BASE_URL}/index.html",
            "code": auth_code,
        }
        kakao_token = requests.post(
            kakao_token_api,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=data,
        )
        access_token = kakao_token.json().get("access_token")
        user_data = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
            },
        )
        user_data = user_data.json()
        new_account = "K" + str(uuid.uuid4()).replace("-", "")[:10]
        data = {
            "account": new_account,
            "email": user_data.get("kakao_account").get("email"),
            "nickname": user_data.get("properties").get("nickname"),
            "signup_type": "카카오",
            "is_active": True,
        }
        return SocialLogin(**data)


''' 네이버로그인 '''
class NaverLoginView(APIView):
    def get(self, request):
        return Response(config("NAVER_LOGIN_API_KEY"), status=status.HTTP_200_OK)

    def post(self, request):
        code = request.data.get("naver_code")
        state = request.data.get("state")
        NAVERLOGINAPIKEY = config("NAVER_LOGIN_API_KEY")
        access_token = requests.post(
            f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&code={code}&client_id={NAVERLOGINAPIKEY}&client_secret={NAVERLOGINAPIKEY}&state={state}",
            headers={"Accept": "application/json"},
        )
        access_token = access_token.json().get("access_token")
        user_data = requests.get(
            "https://openapi.naver.com/v1/nid/me",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )
        user_data = user_data.json().get("response")
        new_account = "N" + str(uuid.uuid4()).replace("-", "")[:10]
        data = {
            "account": new_account,
            # "email": user_data.get("email"),
            "nickname": user_data["nickname"],
            "signup_type": "네이버",
        }
        return SocialLogin(**data)


''' 구글로그인 '''
class GoogleLoginView(APIView):
    def get(self, request):
        GOOGLELOGINAPIKEY = config("GOOGLE_LOGIN_API_KEY")
        return Response(GOOGLELOGINAPIKEY, status=status.HTTP_200_OK)

    def post(self, request):
        access_token = request.data["access_token"]
        user_data = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = user_data.json()
        new_account = "G" + str(uuid.uuid4()).replace("-", "")[:10]
        data = {
            "account": new_account,
            "email": user_data.get("email"),
            "nickname": user_data.get("name"),
            "signup_type": "구글",
            "is_active": True,
        }
        return SocialLogin(**data)


''' 로그인 '''
def SocialLogin(**kwargs):
    data = {key: value for key, value in kwargs.items() if value is not None}
    email = data.get("email")
    signup_type = data.get("signup_type")
    if not email:
        return Response(
            {"error": "해당 계정에 email정보가 없습니다."}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user = User.objects.get(email=email)
        if signup_type == user.signup_type:
            refresh = RefreshToken.for_user(user)
            access_token = CustomTokenObtainPairSerializer.get_token(user)
            return Response(
                {"refresh": str(refresh), "access": str(access_token.access_token)},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": f"{user.signup_type}회원가입으로 이미 가입된 계정이 있습니다!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    # 유저가 존재하지 않는다면 회원가입
    except User.DoesNotExist:
        user = User.objects.create(**data)
        # 비밀번호 사용 불가
        user.set_unusable_password()
        user.save()

        # Profile 객체 생성
        Profile.objects.create(user=user)

        # 토큰 발급
        refresh = RefreshToken.for_user(user)
        access_token = CustomTokenObtainPairSerializer.get_token(user)
        return Response(
            {"refresh": str(refresh), "access": str(access_token.access_token)},
            status=status.HTTP_200_OK,
        )


""" 소셜 로그인 끝 """


""" 현재 지역 시작 """

class RegionView(APIView):
    def patch(self, request):
        user = get_object_or_404(User, id=int(request.data["user"]))
        profile = get_object_or_404(Profile, user=user)

        serializer = ProfileRegionSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "프로필 수정이 완료되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


""" 현재 지역 끝 """


""" 신고하기 """
class ReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        try:
            report_user = get_object_or_404(User, id=request.user.id)
            reported_user = get_object_or_404(User, id=user_id)

            Report.objects.create(report_user=report_user, reported_user=reported_user)

            reported_user.warning += 1

            # 신고누적차단
            if reported_user.warning >= 1:
                reported_user.is_active = False
                reported_user.is_blocked = True
                blocked_check = Blacklist.objects.filter(blocked_user=reported_user)
                if blocked_check.exists():
                    current_block_count = blocked_check.last().blocked_count + 1
                    Blacklist.objects.create(
                        blocked_user=reported_user, blocked_count=current_block_count
                    )
                else:
                    Blacklist.objects.create(blocked_user=reported_user)

            reported_user.save()

            return Response({"message": "신고완료"}, status=status.HTTP_200_OK)

        except IntegrityError:
            return Response({"message": "중복신고불가"}, status=status.HTTP_400_BAD_REQUEST)
