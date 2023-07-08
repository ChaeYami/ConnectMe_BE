# chat/views.py
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import ChatRoom
from user.models import Profile

from .serializers import ChatRoomSerializer, ChatListSerializer


class ChatRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = request.user
        chat_list = ChatRoom.objects.filter(Q(participant1=user) | Q(participant2=user))
        serializer = ChatListSerializer(chat_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        user1 = request.user.id
        user2 = user_id
        participants = [user1, user2]
        sorted_participants = sorted(participants)
        room_name = "n".join(map(str, sorted_participants))

        participant1_profile = get_object_or_404(
            Profile, user_id=sorted_participants[0]
        )
        participant2_profile = get_object_or_404(
            Profile, user_id=sorted_participants[1]
        )

        chat_room = ChatRoom.objects.filter(
            Q(participant1=sorted_participants[0])
            & Q(participant2=sorted_participants[1])
            & Q(participant1_profile=participant1_profile)
            & Q(participant2_profile=participant2_profile)
            & Q(room_name=room_name)
        )

        # DB 정리용 임시 코드
        chat_room_delete1 = ChatRoom.objects.filter(
            Q(participant1_profile=None) | Q(participant2_profile=None)
        )
        chat_room_delete1.delete()

        chat_room_delete2 = ChatRoom.objects.filter(
            Q(participant1=sorted_participants[1])
            & Q(participant2=sorted_participants[0])
            & Q(room_name=room_name)
        )
        chat_room_delete2.delete()

        if not chat_room.exists():
            data = {
                "room_name": room_name,
                "participant1": sorted_participants[0],
                "participant2": sorted_participants[1],
                "participant1_profile": participant1_profile.id,
                "participant2_profile": participant2_profile.id,
            }
            serializer = ChatRoomSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = {
                "room_name": room_name,
                "participant1": sorted_participants[0],
                "participant2": sorted_participants[1],
                "participant1_profile": participant1_profile.id,
                "participant2_profile": participant2_profile.id,
            }
            return Response(data, status=status.HTTP_200_OK)
