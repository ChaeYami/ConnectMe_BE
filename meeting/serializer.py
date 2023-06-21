from rest_framework import serializers

from meeting.models import (
    Meeting,
    MeetingComment,
    MeetingCommentReply,
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
    created_at = serializers.DateTimeField(format="%Y/%m/%d %H:%M")
    updated_at = serializers.DateTimeField(format="%Y/%m/%d %H:%M")
    def get_user(self, obj):
        return obj.user.nickname
    
    class Meta:
        model = MeetingCommentReply
        fields = "__all__"

# 모임 댓글 리스트
class MeetingCommentListSerializer(serializers.ModelSerializer):
    reply = MeetingCommentReplyListSerializer(many=True) # 대댓글 Nested Serializer
    created_at = serializers.DateTimeField(format="%Y/%m/%d %H:%M")
    updated_at = serializers.DateTimeField(format="%Y/%m/%d %H:%M")
    user = serializers.SerializerMethodField()
    def get_user(self, obj):
        return obj.user.nickname
    
    class Meta:
        model = MeetingComment
        fields = "__all__"

# ================================ 댓글, 대댓글 Nested Serializer 끝 ================================

# ================================ 모임 글 리스트, 작성, 상세, 수정 ================================
# 모임 글 리스트
class MeetingListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y/%m/%d %H:%M")
    comment_count = serializers.SerializerMethodField()
    meeting_image = MeetingImageSerializer(many=True, read_only=True)

    def get_comment_count(self, obj):
        return obj.comment.count()

    def get_user(self, obj):
        return obj.user.nickname

    class Meta:
        model = Meeting
        fields = ("id","title","user","comment_count","created_at","meeting_image","content","bookmark",)

# 모임 글 작성
class MeetingCreateSerializer(serializers.ModelSerializer):
    meeting_image = MeetingImageSerializer(many=True, read_only=True)

    class Meta:
        model = Meeting
        fields = ("id","title","content","meeting_image",)

    def create(self, validated_data):
        instance = Meeting.objects.create(**validated_data)
        image_set = self.context['request'].FILES
        for image_data in image_set.getlist('image'):
            MeetingImage.objects.create(meeting=instance, image=image_data)
        return instance

    

# 모임 글 수정
class MeetingUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Meeting
        fields = ("title","content",)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        
        image_set = self.context['request'].FILES
        for image_data in image_set.getlist('image'):
            MeetingImage.objects.create(meeting=instance, image=image_data)
        return instance
    
        

# 모임 글 상세
class MeetingDetailSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y/%m/%d %H:%M")
    updated_at = serializers.DateTimeField(format="%Y/%m/%d %H:%M")
    user = serializers.SerializerMethodField()
    comment = MeetingCommentListSerializer(many=True) # 댓글 Nested Serializer
    meeting_image = MeetingImageSerializer(many=True, read_only=True)
    def get_user(self, obj):
        return obj.user.nickname
    
    class Meta:
        model = Meeting
        fields = "__all__"

# ================================ 모임 글 리스트, 작성, 상세, 수정 끝 ================================

# ================================ 모임 댓글 작성, 수정 ================================

# 모임 댓글 작성 수정
class MeetingCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingComment
        fields = ("content",)

# ================================ 모임 댓글 작성, 수정 끝 ================================

# ================================ 모임 대댓글 목록, 작성, 수정 시작 ================================
class MeetingCommentReplyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingCommentReply
        fields = "__all__"

# 모임 대댓글 작성 수정
class MeetingCommentReplyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingCommentReply
        fields = ("content",)

# ================================ 모임 대댓글 작성, 수정 끝 ================================