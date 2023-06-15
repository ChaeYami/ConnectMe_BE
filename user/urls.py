from django.urls import path
from user import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # user
    path("", views.UserView.as_view(), name="user_view"),  # /user/ : 회원가입, 정보수정, 회원탈퇴
    path("verify-email/b'<str:uidb64>'/<str:token>/", views.VerifyEmailView.as_view(), name="verify_email_view"),  # /user/verify-email/uidb64/token/ : 회원가입 이메일 인증
    
    path("login/", views.CustomTokenObtainPairView.as_view(), name="login_view"),  # /user/login/ : 로그인
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("password/change/", views.ChangePasswordView.as_view(), name="password_change_view"), #/user/password/change/ : 비밀번호 변경
    
    # sms 
    path("send-phone/", views.CertifyPhoneView.as_view, name = "certify_phone_view"), # /user/send-phone/ : sms 인증번호 발송
    path("vertify-phone/signin/",views.ConfirmPhoneNumberView.as_view(), name = "vertify_phone_view"), # /user/vertify-phone/signin/ : 회원가입 전화번호 인증
    path("vertify-phone/account/", views.ConfirmAccountView.as_view, name = "find_account_view"), # /user/vertify-phone/account/ : 아이디 찾기 sms 인증
    
    # social login
    path("login/kakao/", views.KakaoLoginView.as_view(), name="kakao_login_view"),
    path("login/naver/", views.NaverLoginView.as_view(), name="naver_login_view"),
    path("login/google/", views.GoogleLoginView.as_view(), name="google_login_view"),
    
    # profile
    path("profile/<int:user_id>/", views.ProfileView.as_view(), name="profile_view"), # /user/profile/id/ : 프로필
    path("<int:user_id>/image/<int:image_id>/", views.ProfileAlbumView.as_view(), name="profile_album_view"), # /user/id/image : 사진첩
    
    # recommend
    path("recommend/<str:filter>/", views.ProfileListView.as_view(), name = "recommend_view" ), # /user/recommend/filter : 유저 추천
    
    # friend
    path('friend/<int:user_id>/', views.FriendView.as_view(), name='friend_request_view'), # user/friend/id/ : 친구신청 로그
    path('friend/<int:friend_request_id>/accept/', views.FriendAcceptView.as_view(), name='friend_request_accept_view'),# user/friend/id/accept/ : 친구신청 수락
    path('friend/<int:friend_request_id>/reject/', views.FriendRejectView.as_view(), name='friend_request_reject_view'),# user/friend/id/reject/ : 친구신청 거절
    path('friend/request-list/', views.RequestList.as_view(), name="received_list"),
    path('friend/list/', views.FriendsListView.as_view(), name = "friends_list"),
    
    # password
    path("password/email/", views.PasswordResetView.as_view(), name="password_reset"),  # /user/password/email : 비밀번호 찾기 (이메일 보내기)
    path("password/reset/",views.SetNewPasswordView.as_view(),name="password_reset_confirm"),  # /user/password/reset/비밀번호 재설정
    
    # current_region
    path("region/", views.RegionView.as_view(), name="region_view"), # /user/region/ : 현재 지역 입력값
    
    
]