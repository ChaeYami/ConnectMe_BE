from django.urls import path

from . import views

app_name = 'counsel'

#ConnetMe/urls.py파일에서 counsel/에 대한 처리를 한 상태에서 counsel/가 아닌
#빈 문자열을 인자로 넘겨 줌
urlpatterns = [
    path('', views.index, name='index'), 
    path('<int:question_id>/', views.detail, name='detail'),
    path('answer/user_id/<int:question_id>/', views.user_id, name='user_id'),
    path('question/user_id/', views.user_id, name='user_id'),
]
