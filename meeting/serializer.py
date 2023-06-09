from rest_framework import serializers

from meeting.models import (
    Meeting, MeetingComment
    )
# ================================ 모임 댓글 리스트 ================================
# 따로 위에 올려놓은 이유는 모임 글 상세에 Nested Serializer 사용하기 위함입니다.
#모임 댓글 리스트
class MeetingCommentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingComment
        fields = ("user","content","updated_at",)

# ================================ 모임 글 리스트, 작성, 상세, 수정 ================================

#모임 글 리스트,
class MeetingListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField
    def get_user(self, obj):
        return obj.user.nickname

    class Meta:
        model = Meeting
        fields = ("title","user","created_at",)

#모임 글 작성, 수정
class MeetingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ("title","content",)

#모임 글 상세
class MeetingDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField
    comment = MeetingCommentListSerializer(many=True) #여기가 Nested Serializer
    def get_user(self, obj):
        return obj.user.nickname
    
    class Meta:
        model = Meeting
        fields = ("title","content","user","comment",)

# ================================ 모임 글 리스트, 작성, 상세, 수정 끝 ================================

# ================================ 모임 댓글 작성, 수정 ================================

#모임 댓글 작성 수정
class MeetingCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingComment
        fields = ("content",)

# ================================ 모임 댓글 작성, 수정 끝 ================================