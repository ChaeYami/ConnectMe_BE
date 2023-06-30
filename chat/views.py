# chat/views.py
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import ChatRoom

from .serializers import ChatRoomSerializer


class ChatRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        participant1 = request.user.id
        participant2 = user_id
        participants = [participant1, participant2]
        sorted_participants = sorted(participants)
        room_name = "n".join(map(str, sorted_participants))

        chat_room = ChatRoom.objects.filter(
            Q(participant1=participant1)
            & Q(participant2=participant2)
            & Q(room_name=room_name)
        )

        if not chat_room.exists():
            data = {
                "room_name": room_name,
                "participant1": participant1,
                "participant2": participant2,
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
                "participant1": participant1,
                "participant2": participant2,
            }
            return Response(data, status=status.HTTP_200_OK)
