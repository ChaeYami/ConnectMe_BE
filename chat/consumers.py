from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from .models import ChatMessage, ChatRoom
from user.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def fetch_messages(self, data):
        room_name = data["room_name"]
        messages = await database_sync_to_async(ChatMessage.last_50_messages)(room_name)
        content = {
            "command": "messages",
            "messages": await self.messages_to_json(messages),
        }
        await self.send_message(content)

    async def new_message(self, data):
        room_name = data["room_name"]
        chat_room = await database_sync_to_async(
            ChatRoom.objects.filter(room_name=room_name).first
        )()
        author = data["from"]
        author_user = await database_sync_to_async(
            User.objects.filter(nickname=author).first
        )()
        message = await database_sync_to_async(ChatMessage.objects.create)(
            chat_room=chat_room, author=author_user, content=data["message"]
        )
        content = {
            "command": "new_message",
            "message": self.message_to_json(message),
        }
        return await self.send_chat_message(content)

    @database_sync_to_async
    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            "author": message.author.nickname,
            "content": message.content,
            "timestamp": str(message.timestamp),
        }

    commands = {"fetch_messages": fetch_messages, "new_message": new_message}

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.commands[data["command"]](self, data)

    async def send_chat_message(self, message):
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    async def send_message(self, message):
        await self.send(text_data=json.dumps(message))

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps(message))
