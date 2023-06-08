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
    SignupSerializer,
    CustomTokenObtainPairSerializer,
    UserDelSerializer,
    PasswordResetSerializer,
    SetNewPasswordSerializer,
    EmailThread,
    UserUpdateSerializer,
)

from .models import User, Profile


# ================================ 회원가입, 회원정보 시작 ================================
class UserView(APIView):
    permission_classes = [AllowAny]
    
    def get_permissions(self):
        if self.request.method == "PUT" or self.request.method == "DELETE":
            return [IsAuthenticated(),]
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
       
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 회원정보수정
    def patch (self, request):
        user = get_object_or_404(User, id=request.user.id)
        serializer = UserUpdateSerializer(user, data=request.data, context={"request": request}, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "수정완료!"}, status=status.HTTP_200_OK)
        
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