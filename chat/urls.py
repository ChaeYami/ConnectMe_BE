from django.urls import path
from chat import views

urlpatterns = [
    path("<int:user_id>/", views.ChatRoomView.as_view(), name="chat_room_view"),
]
