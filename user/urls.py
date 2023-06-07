from django.urls import path
from user import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("", views.UserView.as_view(), name="sign_up_view"),  # /user/ : 회원가입, 정보수정, 회원탈퇴
    path("login/", views.CustomTokenObtainPairView.as_view(), name="login_view"),  # /user/login/ : 로그인
]