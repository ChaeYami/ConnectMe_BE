from base64 import urlsafe_b64encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.hashers import check_password
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_bytes, force_str
from django.db.models.query_utils import Q
from django.core.mail import EmailMessage

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework import serializers, exceptions
from user.models import User, Profile
from user.validators import (
    password_validator,
    password_pattern,
    account_validator,
    nickname_validator,
    phone_validator
)

import threading

from django.conf import settings



# ================================ SignupSerializer 회원가입(user serializser) ================================ 

# 기왕 프로필 페이지와 모델도 분리한김에 시리얼라이저 이름도 UserSerializer 대신에 SignupSerializer 로 했습니당
class SignupSerializer(serializers.ModelSerializer):
    joined_at = serializers.SerializerMethodField()
    
    def get_joined_at(self, obj):
        return obj.joined_at.strftime("%Y년 %m월 %d일")
    
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "account": {
                "error_messages": {
                    "required": "ID는 필수 입력 사항입니다.",
                    "blank": "ID는 필수 입력 사항입니다.",
                }
            },
            "password": {
                "write_only": True,
                "error_messages": {
                    "required": "비밀번호는 필수 입력 사항입니다.",
                    "blank": "비밀번호는 필수 입력 사항입니다.",
                },
            },
            "phone": {
                "error_messages": {
                    "required": "전화번호는 필수 입력 사항입니다.",
                    "invalid": "알맞은 형식의 전화번호를 입력해주세요.",
                    "blank": "전화번호는 필수 입력 사항입니다.",
                },
            },
            "email": {
                "error_messages": {
                    "required": "이메일은 필수 입력 사항입니다.",
                    "invalid": "알맞은 형식의 이메일을 입력해주세요.",
                    "blank": "이메일은 필수 입력 사항입니다.",
                }
            },
            "nickname": {
                "error_messages": {
                    "required": "닉네임은 필수 입력 사항입니다.",
                    "invalid": "알맞은 형식의 닉네임을 입력해주세요.",
                    "blank": "닉네임은 필수 입력 사항입니다.",
                }
            },
            "is_admin": {
                "write_only": True,
            },
            "is_active": {
                "write_only": True,
            },
        }
    
    def validate(self,data):
        account = data.get("account")
        password = data.get("password")
        nickname = data.get("nickname")
        phone = data.get("phone")
        
    # 아이디 유효성 검사
        if account_validator(account):
            raise serializers.ValidationError(
                detail={"username": "아이디는 5자 이상 20자 이하의 숫자, 영문 대/소문자를 포함해야 합니다."}
            )

        # 비밀번호 유효성 검사
        if password_validator(password):
            raise serializers.ValidationError(
                detail={"password": "비밀번호는 8자 이상의 영문 대/소문자와 숫자, 특수문자를 포함해야 합니다."}
            )

        # 비밀번호 유효성 검사
        if password_pattern(password):
            raise serializers.ValidationError(
                detail={"password": "비밀번호는 연속해서 3자리 이상 동일한 영문,숫자,특수문자 사용이 불가합니다."}
            )
            
        if phone_validator(phone):
            raise serializers.ValidationError(
                detail={"phone": "전화번호는 숫자만 사용해주세요."}
            )
            
        if nickname_validator(nickname):
            raise serializers.ValidationError(
                detail={"nickname": "닉네임은 공백 없이 2자이상 8자 이하의 영문, 한글, 특수문자는 '-' 와 '_'만 사용 가능합니다."}
            )

        return data
    
    # 회원가입
    def create(self, validated_data):
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        
        Profile.objects.create(user = user)
        
        return user
        
# ================================ 회원가입(user serializser) 끝 ================================ 

        

# ================================ 정보수정(이메일, 전화번호) 시작 ================================ 

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email","phone")
        extra_kwargs = {
            "email": {
                "error_messages": {
                    "required": "이메일을 입력해주세요.",
                    "invalid": "알맞은 형식의 이메일을 입력해주세요.",
                    "blank": "이메일을 입력해주세요.",
                }
            },
            "phone": {
                "error_messages": {
                    "required": "전화번호를 입력해주세요.",
                    "invalid": "알맞은 형식의 전화번호를 입력해주세요.",
                    "blank": "전화번호를 입력해주세요.",
                }
            },
        }
        
    def validate(self, data):
        phone = data.get("phone")
        current_phone = self.context.get("request").user.phone

        # 휴대폰 번호 존재여부와 blank 허용
        if (User.objects.filter(phone=phone).exclude(phone=current_phone).exists() and not phone == ""):
            raise serializers.ValidationError(detail={"phone": "이미 사용중인 휴대폰 번호 이거나 탈퇴한 휴대폰 번호입니다."})

        return data

    
    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.phone = validated_data.get("phone", instance.phone)
        instance.save()
        
        return instance
    
    
# ================================ 정보수정(이메일, 전화번호) 끝 ================================ 


# 로그인 토큰 serializer
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["account"] = user.account
        token["phone"] = user.phone
        token["nickname"] = user.nickname
        return token

    def get_user(self, validated_data):
        user = self.user
        return user

# 회원탈퇴 serializer
class UserDelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("is_active",)

# ==============================================================================================================
class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Util:
    @staticmethod
    def send_email(message):
        email = EmailMessage(
            subject=message["email_subject"],
            body=message["email_body"],
            to=[message["to_email"]],
        )
        EmailThread(email).start()


# ==============================================================================================================

# 비밀번호 변경 serializer
class ChangePasswordSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        error_messages={
            "required": "비밀번호를 입력해주세요.",
            "blank": "비밀번호를 입력해주세요.",
            "write_only": True,
        }
    )
    repassword = serializers.CharField(
        error_messages={
            "required": "비밀번호를 입력해주세요.",
            "blank": "비밀번호를 입력해주세요.",
            "write_only": True,
        }
    )

    class Meta:
        model = User
        fields = (
            "password",
            "repassword",
            "confirm_password",
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
                "error_messages": {
                    "required": "비밀번호를 입력해주세요.",
                    "blank": "비밀번호를 입력해주세요.",
                },
            },
        }

    def validate(self, data):
        current_password = self.context.get("request").user.password
        confirm_password = data.get("confirm_password")
        password = data.get("password")
        repassword = data.get("repassword")

        # 현재 비밀번호 예외 처리
        if not check_password(confirm_password, current_password):
            raise serializers.ValidationError(detail={"password": "현재 비밀번호가 일치하지 않습니다."})

        # 현재 비밀번호와 바꿀 비밀번호 비교
        if check_password(password, current_password):
            raise serializers.ValidationError(detail={"password": "현재 사용중인 비밀번호와 동일한 비밀번호는 입력할 수 없습니다."})

        # 비밀번호 일치
        if password != repassword:
            raise serializers.ValidationError(detail={"password": "비밀번호가 일치하지 않습니다."})

        # 비밀번호 유효성 검사
        if password_validator(password):
            raise serializers.ValidationError(detail={"password": "비밀번호는 8자 이상 16자이하의 영문 대/소문자, 숫자, 특수문자 조합이어야 합니다. "})

        # 비밀번호 문자열 동일여부 검사
        if password_pattern(password):
            raise serializers.ValidationError(detail={"password": "비밀번호는 3자리 이상 동일한 영문/사용 사용 불가합니다. "})

        return data

    def update(self, instance, validated_data):
        instance.password = validated_data.get("password", instance.password)
        instance.set_password(instance.password)
        instance.save()

        return instance
    
# ================================ 비밀번호 재설정 시작 ================================ 

# 비밀번호 찾기 serializer
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ("email",)

    def validate(self, attrs):
        try:
            email = attrs.get("email")

            user = User.objects.get(email=email)
            uidb64 = urlsafe_b64encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)

            frontend_site = "127.0.0.1:5500"
            absurl = f"http://{frontend_site}/user/set_password.html?id=${uidb64}&token=${token}"

            email_body = "비밀번호 재설정을 위해 아래 링크를 클릭해주세요. \n " + absurl
            message = {
                "email_body": email_body,
                "to_email": user.email,
                "email_subject": "비밀번호 재설정",
            }
            Util.send_email(message)

            return super().validate(attrs)

        except User.DoesNotExist:
            raise serializers.ValidationError(
                detail={"email": "잘못된 이메일입니다. 다시 입력해주세요."}
            )


# 비밀번호 재설정 serializer
class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True,
    )
    repassword = serializers.CharField(
        write_only=True,
    )
    token = serializers.CharField(
        max_length=100,
        write_only=True,
    )
    uidb64 = serializers.CharField(
        max_length=100,
        write_only=True,
    )

    class Meta:
        fields = (
            "repassword",
            "password",
            "token",
            "uidb64",
        )

    def validate(self, attrs):
        password = attrs.get("password")
        repassword = attrs.get("repassword")
        token = attrs.get("token")
        uidb64 = attrs.get("uidb64")

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)

            if PasswordResetTokenGenerator().check_token(user, token) == False:
                raise exceptions.AuthenticationFailed("토큰이 유효하지 않습니다.", 401)
            if password != repassword:
                raise serializers.ValidationError(
                    detail={"repassword": "비밀번호가 일치하지 않습니다."}
                )
            # 비밀번호 유효성 검사
            if password_validator(password):
                raise serializers.ValidationError(
                    detail={"password": "비밀번호는 8자 이상의 영문 대/소문자와 숫자, 특수문자를 포함하여야 합니다."}
                )

            # 비밀번호 유효성 검사
            if password_pattern(password):
                raise serializers.ValidationError(
                    detail={"password": "비밀번호는 연속해서 3자리 이상 동일한 영문,숫자,특수문자 사용이 불가합니다."}
                )

            user.set_password(password)
            user.save()

            return super().validate(attrs)

        except User.DoesNotExist:
            raise serializers.ValidationError(detail={"user": "존재하지 않는 회원입니다."})


# ================================ 비밀번호 재설정 끝 ================================ 


# ================================ 프로필 시작 ================================ 

# 프로필 serializer
class ProfileSerializer(serializers.ModelSerializer):
    account = serializers.SerializerMethodField()
    nickname = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    
    def get_user_id(self,obj):
        return obj.user.id
    
    def get_account(self,obj):
        return obj.user.account
    
    def get_nickname(self, obj):
        return obj.user.nickname
    
    class Meta:
        model = Profile
        fields = ("id", "user_id", "account", "nickname", "profile_img", "prefer_region", "mbti", "age", "introduce")
        
# 프로필 편집 serializer
class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "nickname",
            "profile_img",
            "introduce",
        )
        extra_kwargs = {
            "nickname": {
                "error_messages": {
                    "invalid": "알맞은 형식의 닉네임을 입력해주세요.",
                    "blank": "닉네임은 필수 입력 사항입니다.",
                }
            },
            
        }

    def validate(self, data):
        nickname = data.get("nickname")

        # 닉네임 유효성 검사
        if nickname_validator(nickname):
            raise serializers.ValidationError(detail={"nickname": "닉네임은 공백 없이 2자이상 8자 이하의 영문, 한글,'-' 또는'_'만 사용 가능합니다."})

        return data

    def update(self, instance, validated_data):
        instance.nickname = validated_data.get("nickname", instance.nickname)
        instance.profile_img = validated_data.get("profile_img", instance.profile_img)
        instance.introduce = validated_data.get("introduce", instance.introduce)
        instance.save()

        return instance