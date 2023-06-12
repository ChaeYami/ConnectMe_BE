from rest_framework import serializers

from meeting.models import (
    Meeting,
    MeetingComment,
    MettingCommentReply,
    MeetingImage,
    )

# ================================ 모임 이미지 시작 ================================ 

class MeetingImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = MeetingImage
        fields = "__all__"

# ================================ 모임 이미지 끝 ================================ 

# ================================ 댓글, 대댓글 Nested Serializer 시작 ================================
# 따로 위에 올려놓은 이유는 모임 글 상세에 Nested Serializer 사용하기 위함입니다.
# 모임 대댓글 리스트

class MeetingCommentReplyListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    def get_user(self, obj):
        return obj.user.nickname
    
    class Meta:
        model = MettingCommentReply
        fields = ("user","content","updated_at",)

# 모임 댓글 리스트
class MeetingCommentListSerializer(serializers.ModelSerializer):
    reply = MeetingCommentReplyListSerializer(many=True) # 대댓글 Nested Serializer

    user = serializers.SerializerMethodField()
    def get_user(self, obj):
        return obj.user.nickname
    
    class Meta:
        model = MeetingComment
        fields = ("user","content","updated_at","reply",)

# ================================ 댓글, 대댓글 Nested Serializer 끝 ================================

# ================================ 모임 글 리스트, 작성, 상세, 수정 ================================
# 모임 글 리스트
class MeetingListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y/%m/%d")
    def get_user(self, obj):
        return obj.user.nickname

    class Meta:
        model = Meeting
        fields = "__all__"
        # fields = ("id","title","user","created_at",)

# 모임 글 작성, 수정
class MeetingCreateSerializer(serializers.ModelSerializer):
    meeting_image = MeetingImageSerializer(many=True, read_only=True)

    class Meta:
        model = Meeting
        fields = ("title","content","meeting_image",)

    def create(self, validated_data):
        instance = Meeting.objects.create(**validated_data)
        image_set = self.context['request'].FILES
        for image_data in image_set.getlist('image'):
            MeetingImage.objects.create(meeting=instance, image=image_data)
        return instance

# 모임 글 상세
class MeetingDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    comment = MeetingCommentListSerializer(many=True) # 댓글 Nested Serializer
    meeting_image = MeetingImageSerializer(many=True, read_only=True)
    def get_user(self, obj):
        return obj.user.nickname
    
    class Meta:
        model = Meeting
        fields = ("title","content","user","comment","meeting_image",)

# ================================ 모임 글 리스트, 작성, 상세, 수정 끝 ================================

# ================================ 모임 댓글 작성, 수정 ================================

# 모임 댓글 작성 수정
class MeetingCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingComment
        fields = ("content",)

# ================================ 모임 댓글 작성, 수정 끝 ================================

# ================================ 모임 대댓글 작성, 수정 시작 ================================

# 모임 대댓글 작성 수정
class MeetingCommentReplyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MettingCommentReply
        fields = ("content",)

# ================================ 모임 대댓글 작성, 수정 끝 ================================