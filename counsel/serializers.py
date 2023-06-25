from rest_framework import serializers
from .models import (
    Counsel,
    CounselComment,
    CounselReply
)

# ================================ 대댓글 ================================

# 대댓글 작성
class CounselReplyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CounselReply
        fields = ("content",)
        extra_kwargs = {
            "content": {
                "error_messages": {
                    "required": "댓글을 입력해주세요.",
                    "blank": "댓글을 입력해주세요.",
                }
            },
        }

# 대댓글
class CounselReplySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    reply_like_count = serializers.SerializerMethodField()
    comment_created_at = serializers.DateTimeField(
        format="%y-%m-%d %H:%M", read_only=True
    )
    def get_reply_like_count(self, obj):
        return obj.like.count()

    def get_user(self, obj):
        return {"nickname": obj.user.nickname, "pk": obj.user.pk}

    class Meta:
        model = CounselReply
        fields = "__all__"

# ================================ 댓글 ================================

class CounselCommentSerializer(serializers.ModelSerializer):
    reply = CounselReplySerializer(many=True)
    user = serializers.SerializerMethodField()
    comment_like_count = serializers.SerializerMethodField()
    comment_created_at = serializers.DateTimeField(
        format="%y-%m-%d %H:%M", read_only=True
    )

    def get_user(self, obj):
        return obj.user.account
    
    def get_comment_like_count(self, obj):
        return obj.like.count()

    class Meta:
        model = CounselComment
        fields = "__all__"

# 댓글 작성
class CounselCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CounselComment
        fields = ("content",)
        extra_kwargs = {
            "content": {
                "error_messages": {
                    "required": "댓글을 입력해주세요.",
                    "blank": "댓글을 입력해주세요.",
                }
            },
        }


# ================================ 글 작성, 상세, 수정 ================================
# 글 리스트
class CounselListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y년 %m월 %d일 %H시 %M분")
    
    def get_user(self, obj):
        return obj.user.account

    class Meta:
        model = Counsel
        fields = "__all__"

        

# 글 작성, 수정
class CounselCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Counsel
        exclude = ['user', 'like', 'created_at', 'updated_at']
        extra_kwargs={
            "title": {
                "error_messages": {
                    "blank": "제목을 입력해주세요",
                }
            },
            "content": {
                "error_messages": {
                    "blank": "내용을 입력해주세요",
                },
            },
        }

# 글 상세
class CounselDetailSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y년 %m월 %d일 %H시 %M분")
    updated_at = serializers.DateTimeField(format="%Y년 %m월 %d일 %H시 %M분")
    user = serializers.SerializerMethodField()
    counsel_comment_counsel = CounselCommentSerializer
    def get_user(self, obj):
        return {"account": obj.user.account, "pk": obj.user.pk}
    
    class Meta:
        model = Counsel
        fields = "__all__"




