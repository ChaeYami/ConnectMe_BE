from rest_framework import serializers

from meeting.models import Meeting

class MeetingListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField

    def get_user(self, obj):
        return obj.user.nickname

    class Meta:
        model = Meeting
        fields = ("title","user","created_at")

class MeetingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ("title","content")

class MeetingDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField

    def get_user(self, obj):
        return obj.user.nickname
    
    class Meta:
        model = Meeting
        fields = ("title","content","user")