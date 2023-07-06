from rest_framework import serializers
from .models import (
    Counsel,
    CounselComment,
    CounselReply
)

import bleach

""" 대댓글 """

'''대댓글 작성'''
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
        
    def validate(self, attrs):
        content = attrs.get('content')
        # content 필드에서 HTML 태그 제거
        cleaned_content = bleach.clean(content, tags=[], strip=True)

        attrs['content'] = cleaned_content

        return attrs

'''대댓글'''
class CounselReplySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    reply_like_count = serializers.SerializerMethodField()
    updated_at = serializers.DateTimeField(
        format="%y.%m.%d %H:%M", read_only=True
    )
    def get_reply_like_count(self, obj):
        return obj.like.count()

    def get_user(self, obj):
        return {"nickname": obj.user.nickname, "pk": obj.user.pk}

    class Meta:
        model = CounselReply
        fields = "__all__"
        

""" 댓글 """

class CounselCommentSerializer(serializers.ModelSerializer):
    reply = CounselReplySerializer(many=True)
    user = serializers.SerializerMethodField()
    comment_like_count = serializers.SerializerMethodField()
    updated_at = serializers.DateTimeField(
        format="%y.%m.%d %H:%M", read_only=True
    )

    def get_user(self, obj):
        return {"account": obj.user.account, "pk": obj.user.pk, "nickname": obj.user.nickname}
    
    def get_comment_like_count(self, obj):
        return obj.like.count()

    class Meta:
        model = CounselComment
        fields = "__all__"
        
    

'''댓글 작성'''
class CounselCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CounselComment
        fields = ("content","is_anonymous",)
        extra_kwargs = {
            "content": {
                "error_messages": {
                    "required": "댓글을 입력해주세요.",
                    "blank": "댓글을 입력해주세요.",
                }
            },
        }

    def validate(self, attrs):
        content = attrs.get('content')

        # content 필드에서 HTML 태그 제거
        cleaned_content = bleach.clean(content, tags=[], strip=True)

        attrs['content'] = cleaned_content

        return attrs
    
""" 글 작성, 상세, 수정 """

'''글 리스트'''
class CounselListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y.%m.%d")
    
    def get_user(self, obj):
        return {"account": obj.user.account, "pk": obj.user.pk, "nickname": obj.user.nickname}
    
    def get_comment_count(self, obj):
        reply_count = CounselReply.objects.filter(comment__in=obj.counsel_comment_counsel.all()).count()
        return obj.counsel_comment_counsel.count()+reply_count

    class Meta:
        model = Counsel
        fields = "__all__"

        

'''글 작성, 수정'''
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
    def validate(self, attrs):
            title = attrs.get('title')
            content = attrs.get('content')

            # title 필드에서 HTML 태그 제거
            cleaned_title = bleach.clean(title, tags=[], strip=True)

            # content 필드에서 HTML 태그 제거
            cleaned_content = bleach.clean(content, tags=[], strip=True)

            attrs['title'] = cleaned_title
            attrs['content'] = cleaned_content

            return attrs
'''글 상세'''
class CounselDetailSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y.%m.%d  %H:%M")
    updated_at = serializers.DateTimeField(format="%Y.%m.%d  %H:%M")
    user = serializers.SerializerMethodField()
    counsel_comment_counsel = CounselCommentSerializer
    def get_user(self, obj):
        return {"account": obj.user.account, "pk": obj.user.pk, "nickname": obj.user.nickname}
    
    class Meta:
        model = Counsel
        fields = "__all__"




