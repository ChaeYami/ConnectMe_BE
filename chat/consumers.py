from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import Q

from .models import ChatMessage, ChatRoom
from user.models import User
from django.conf import settings

import json
import jwt
from datetime import datetime
from urllib.parse import parse_qs


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
        author_id = data["from"]
        author_user = await database_sync_to_async(
            User.objects.filter(id=author_id).first
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

        # 파라미터에서 token 추출
        query_string = self.scope["query_string"].decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        # 토큰이 없을 경우 WebSocket 연결 끊기
        if not token:
            await self.send_alert("로그인 해주세요.")
            await self.close()
            return

        # jwt 토큰 decoding
        try:
            decoded_token = jwt.decode(
                token, key=settings.SECRET_KEY, algorithms=["HS256"], verify=True
            )

        # 토큰이 유효하지 않은 경우 WebSocket 연결 끊기
        except jwt.InvalidTokenError:
            await self.send_alert("로그인이 만료되었습니다.")
            await self.close()
            return

        room_name = self.room_name
        participants = room_name.split("n")
        self.user_id = str(decoded_token["user_id"])
        user_id = self.user_id

        # 채팅방 참가자가 아닐 경우 WebSocket 연결 끊기
        if user_id not in participants:
            await self.send_alert("채팅 참가 권한이 없습니다.")
            await self.close()
            return

        # 채팅방 참가자일 경우 참가 메시지 보내기
        user = await database_sync_to_async(User.objects.filter(id=user_id).first)()
        nickname = user.nickname

        join_message = f"{nickname}님이 채팅방에 참가했습니다."

        message = {
            "author": nickname,
            "content": join_message,
            "timestamp": str(datetime.now()),
        }
        content = {
            "command": "new_message",
            "message": message,
        }
        await self.send_chat_message(content)
        return

    async def disconnect(self, close_code):
        # 채팅방 참가자일 경우 나갈 때 메시지 보내기
        room_name = self.room_name
        participants = room_name.split("n")
        user_id = str(self.user_id)
        if user_id in participants:
            user = await database_sync_to_async(User.objects.filter(id=user_id).first)()
            nickname = user.nickname

            exit_message = f"{nickname}님이 채팅방을 나갔습니다."

            message = {
                "author": nickname,
                "content": exit_message,
                "timestamp": str(datetime.now()),
            }
            content = {
                "command": "new_message",
                "message": message,
            }
            await self.send_chat_message(content)
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

    async def send_alert(self, message):
        await self.send(text_data=json.dumps({"command": "alert", "message": message}))
