from django.db import models
from user.models import User


class ChatRoom(models.Model):
    room_name = models.CharField(max_length=255)
    participant1 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="participant1"
    )
    participant2 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="participant2"
    )

    def __str__(self):
        return self.room_name


class ChatMessage(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.nickname

    @staticmethod
    def last_50_messages(room_name):
        return (
            ChatMessage.objects.filter(chat_room__room_name=room_name)
            .order_by("timestamp")
            .all()[:50]
        )
