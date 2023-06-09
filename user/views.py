from base64 import urlsafe_b64decode, urlsafe_b64encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import authenticate
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import DjangoUnicodeDecodeError, force_str, force_bytes
from django.shortcuts import redirect
from django.core.mail import EmailMessage

from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView

from user.serializers import (
    ChangePasswordSerializer,
    FriendSerializer,
    SignupSerializer,
    CustomTokenObtainPairSerializer,
    UserDelSerializer,
    ProfileSerializer,
    PasswordResetSerializer,
    SetNewPasswordSerializer,
    EmailThread,
    UserUpdateSerializer,
)

from .models import Friend, User, Profile


# ================================ 회원가입, 회원정보 시작 ================================
class UserView(APIView):
    permission_classes = [AllowAny]
    
    def get_permissions(self):
        if self.request.method == "PATCH" or self.request.method == "DELETE":
            return [IsAuthenticated(),]
        else:
            return super(UserView, self).get_permissions()
    
    # 개인정보 보기
    def get(self, request):
        user = get_object_or_404(User, id = request.user.id)
        serializer = SignupSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # 회원가입
    def post(self,request):
        serializer = SignupSerializer(data=request.data)
        
        
        if serializer.is_valid():
           serializer.save()
           return Response({"message" : "회원가입 완료!"} , status=status.HTTP_201_CREATED)
       
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 회원정보수정
    def patch (self, request):
        user = get_object_or_404(User, id=request.user.id)
        serializer = UserUpdateSerializer(user, data=request.data, context={"request": request}, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "수정완료!"}, status=status.HTTP_200_OK)
        
        else:
            return Response( {"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    
    # 회원 탈퇴 (비활성화, 비밀번호 받아서)
    def delete(self, request):
        user = get_object_or_404(User, id=request.user.id)
        datas = request.data.copy()  # request.data → request.data.copy() 변경
        # request.data는 Django의 QueryDict 객체로서 변경이 불가능하여 복사하여 수정한 후 전달하는 방법을 이용!
        datas["is_active"] = False
        serializer = UserDelSerializer(user, data=datas)
        if user.check_password(request.data.get("password")):
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "계정 비활성화 완료"}, status=status.HTTP_204_NO_CONTENT)
            
        else:
            return Response({"message": f"패스워드가 다릅니다"}, status=status.HTTP_400_BAD_REQUEST)

# ================================ 회원가입, 회원정보 끝 ================================


# ================================ 로그인 ================================
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    
# ================================ 비밀번호 변경 ================================
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = get_object_or_404(User, id=request.user.id)
        serializer = ChangePasswordSerializer(user, data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "비밀번호 변경이 완료되었습니다! 다시 로그인해주세요."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# ================================ 프로필 시작 ================================

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    # 요청 유저의 정보를 가져올 때 사용할 get_object 인스턴스 정의
    def get_object(self, user_id):
        return get_object_or_404(User, id=user_id)
    
    # 프로필 보기
    def get(self, request, user_id):
        profile = get_object_or_404(Profile, user = user_id)
        user = get_object_or_404(User, id=user_id)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # 프로필 수정
    def patch(self, request, user_id):
        user = self.get_object(user_id) # 요청 유저의 정보 가져오기
        
        if user == request.user:
            profile = get_object_or_404(Profile, id = user_id)
            serializer = ProfileSerializer(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "프로필 수정이 완료되었습니다."}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response({"message": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)
        
        
        
        
        
# ================================ 프로필 끝 ================================
        
    
    

# ================================ 친구맺기 시작 ================================

# 친구신청
class FriendView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        from_user = request.user
        to_user = get_object_or_404(User, id=user_id)
        serializer = FriendSerializer(data={'from_user': from_user, 'to_user': to_user})
        serializer.is_valid(raise_exception=True)
        friend_request = serializer.save()

        return Response({"message": "친구 신청을 보냈습니다."}, status=status.HTTP_201_CREATED)

# 친구신청 수락
class FriendAcceptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, friend_request_id):
        friend_request = get_object_or_404(Friend, id=friend_request_id)
        if friend_request.to_user != request.user:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        if friend_request.status != 'pending':
            return Response({"message": "이미 처리된 요청입니다."}, status=status.HTTP_400_BAD_REQUEST)

        friend_request.status = 'accepted'
        friend_request.save()

        from_user = friend_request.from_user
        to_user = friend_request.to_user
        from_user.friends.add(to_user)
       
        return Response({"message": "친구 신청을 수락했습니다."}, status=status.HTTP_200_OK)

# 친구신청 거절
class FriendRejectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, friend_request_id):
        friend_request = get_object_or_404(Friend, id=friend_request_id)
        if friend_request.to_user != request.user:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        if friend_request.status != 'pending':
            return Response({"message": "이미 처리된 요청입니다."}, status=status.HTTP_400_BAD_REQUEST)

        friend_request.status = 'rejected'
        friend_request.save()

        return Response({"message": "친구 신청을 거절했습니다."}, status=status.HTTP_200_OK)
    
    

# ================================ 친구맺기 끝 ================================
