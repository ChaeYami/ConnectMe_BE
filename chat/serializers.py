from rest_framework import serializers
from .models import ChatRoom


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = "__all__"


class ChatListSerializer(serializers.ModelSerializer):
    participant1 = serializers.SerializerMethodField()
    participant2 = serializers.SerializerMethodField()
    participant1_profile_img = serializers.SerializerMethodField()
    participant2_profile_img = serializers.SerializerMethodField()

    def get_participant1(self, obj):
        return {"nickname": obj.participant1.nickname, "id": obj.participant1.id}

    def get_participant2(self, obj):
        return {"nickname": obj.participant2.nickname, "id": obj.participant2.id}

    def get_participant1_profile_img(self, obj):
        if obj.participant1_profile and obj.participant1_profile.profile_img:
            return obj.participant1_profile.profile_img.url
        return None

    def get_participant2_profile_img(self, obj):
        if obj.participant2_profile and obj.participant2_profile.profile_img:
            return obj.participant2_profile.profile_img.url
        return None

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "room_name",
            "participant1",
            "participant2",
            "participant1_profile",
            "participant2_profile",
            "participant1_profile_img",
            "participant2_profile_img",
        ]
