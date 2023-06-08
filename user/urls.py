from django.urls import path
from user import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("", views.UserView.as_view(), name="user_view"),  # /user/ : 회원가입, 정보수정, 회원탈퇴
    path("login/", views.CustomTokenObtainPairView.as_view(), name="login_view"),  # /user/login/ : 로그인
    
    path("profile/<int:user_id>/", views.ProfileView.as_view(), name="profile_view"), # /user/profile/ : 프로필
    
    path("password/change/", views.ChangePasswordView.as_view(), name="password_change_view"), #/user/password/change/ : 비밀번호 변경
]