from rest_framework import serializers
import urllib.parse
from PIL import Image

from meeting.models import (
    Meeting,
    MeetingComment,
    MeetingCommentReply,
    MeetingImage,
    )

import bleach


'''모임 이미지 시작'''

class MeetingImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = MeetingImage
        fields = "__all__"

'''모임 이미지 끝'''

'''댓글, 대댓글 Nested Serializer 시작
따로 위에 올려놓은 이유는 모임 글 상세에 Nested Serializer 사용하기 위함입니다.
'''
'''모임 대댓글 리스트'''
class MeetingCommentReplyListSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y.%m.%d %H:%M")
    updated_at = serializers.DateTimeField(format="%Y.%m.%d %H:%M")
    user = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        return {"account": obj.user.account, "pk": obj.user.pk, "nickname": obj.user.nickname}
    
    class Meta:
        model = MeetingCommentReply
        fields = "__all__"

'''모임 댓글 리스트'''
class MeetingCommentListSerializer(serializers.ModelSerializer):
    reply = MeetingCommentReplyListSerializer(many=True) # 대댓글 Nested Serializer
    created_at = serializers.DateTimeField(format="%Y.%m.%d %H:%M")
    updated_at = serializers.DateTimeField(format="%Y.%m.%d %H:%M")
    user = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        return {"account": obj.user.account, "pk": obj.user.pk, "nickname": obj.user.nickname}
    
    class Meta:
        model = MeetingComment
        fields = "__all__"

'''댓글, 대댓글 Nested Serializer 끝'''

'''모임 글 리스트, 작성, 상세, 수정'''
'''모임 글 리스트'''
class MeetingListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y/%m/%d %H:%M")
    comment_count = serializers.SerializerMethodField()
    meeting_image = MeetingImageSerializer(many=True, read_only=True)
    join_meeting_count = serializers.SerializerMethodField()

    def get_join_meeting_count(self, obj):
        return obj.join_meeting.count()

    def get_comment_count(self, obj):
        reply_count = MeetingCommentReply.objects.filter(comment__in=obj.comment.all()).count()
        return obj.comment.count()+reply_count

    def get_user(self, obj):
        return obj.user.nickname

    class Meta:
        model = Meeting
        fields = ("id","title","user","comment_count", "created_at","meeting_image","content","bookmark","meeting_city","meeting_at","num_person_meeting","meeting_status","join_meeting_count",)

'''모임 글 작성'''
class MeetingCreateSerializer(serializers.ModelSerializer):
    meeting_image = MeetingImageSerializer(many=True, read_only=True)

    class Meta:
        model = Meeting
        fields = ("id","place","meeting_city","meeting_at","num_person_meeting","place_title","place_address","title","content","meeting_image","meeting_status",)
        extra_kwargs = {
            
            "meeting_city": {
                "error_messages": {
                    "required": "모임 지역을 선택해주세요.",
                    "blank": "모임 지역을 선택해주세요.",
                }
            },
            "meeting_at": {
                "error_messages": {
                    "required": "모임 날짜를 선택해주세요.",
                    "blank": "모임 날짜를 선택해주세요.",
                }
            },
            "num_person_meeting": {
                "error_messages": {
                    "required": "모집 인원수를 입력해주세요.",
                    "blank": "모집 인원수를 입력해주세요.",
                    "invalid" : "모집 인원수는 2이상 숫자만 입력해주세요.",
                }
            },
            "place_title": {
                "error_messages": {
                    "required": "모임 장소를 입력해주세요.",
                    "blank": "모임 장소를 입력해주세요.",
                }
            },
            "place_address": {
                "error_messages": {
                    "required": "모임 주소를 입력해주세요.",
                    "blank": "모임 주소를 입력해주세요.",
                }
            },
            "title": {
                "error_messages": {
                    "required": "제목을 입력해주세요.",
                    "blank": "제목을 입력해주세요.",
                }
            },
            "content": {
                "error_messages": {
                    "required": "내용을 입력해주세요.",
                    "blank": "내용을 입력해주세요.",
                }
            },
                        
        }

    def validate(self, attrs):
            title = attrs.get('title')
            content = attrs.get('content')
            meeting_city = attrs.get('meeting_city')
            place_title = attrs.get('place_title')
            place_address = attrs.get('place_address')
            cleaned_title = bleach.clean(title, tags=[], strip=True)
            cleaned_content = bleach.clean(content, tags=[], strip=True)
            cleaned_meeting_city = bleach.clean(meeting_city, tags=[], strip=True)
            cleaned_place_title = bleach.clean(place_title, tags=[], strip=True)
            cleaned_place_address = bleach.clean(place_address, tags=[], strip=True)

            attrs['title'] = cleaned_title
            attrs['content'] = cleaned_content
            attrs['meeting_city'] = cleaned_meeting_city
            attrs['place_title'] = cleaned_place_title
            attrs['place_address'] = cleaned_place_address
            
            
            images = self.context['request'].FILES.getlist("image")
            max_size = 1048576  # 1MB
            for image in images:
                img = Image.open(image)
                if image.size > max_size:
                    raise serializers.ValidationError("이미지 크기는 1MB를 초과할 수 없습니다.")

            return attrs
        
    
    def create(self, validated_data):
        instance = Meeting.objects.create(**validated_data)
        image_urls = self.context['request'].data.getlist('image')

        for image_url in image_urls:
            try:
                MeetingImage.objects.create(meeting=instance, image=image_url)
            except Exception as e:
                print(e)
        
        return instance

    

'''모임 글 수정'''
class MeetingUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Meeting
        fields = ("place","meeting_city","meeting_at","num_person_meeting","place_title","place_address","title","content","meeting_status",)      
        extra_kwargs = {
            
            "meeting_city": {
                "error_messages": {
                    "required": "모임 지역을 선택해주세요.",
                    "blank": "모임 지역을 선택해주세요.",
                }
            },
            "meeting_at": {
                "error_messages": {
                    "required": "모임 날짜를 선택해주세요.",
                    "blank": "모임 날짜를 선택해주세요.",
                }
            },
            "num_person_meeting": {
                "error_messages": {
                    "required": "모집 인원수를 입력해주세요.",
                    "blank": "모집 인원수를 입력해주세요.",
                    "invalid" : "모집 인원수는 2이상 숫자만 입력해주세요.",
                }
            },
            "place_title": {
                "error_messages": {
                    "required": "모임 장소를 입력해주세요.",
                    "blank": "모임 장소를 입력해주세요.",
                }
            },
            "place_address": {
                "error_messages": {
                    "required": "모임 주소를 입력해주세요.",
                    "blank": "모임 주소를 입력해주세요.",
                }
            },
            "title": {
                "error_messages": {
                    "required": "제목을 입력해주세요.",
                    "blank": "제목을 입력해주세요.",
                }
            },
            "content": {
                "error_messages": {
                    "required": "내용을 입력해주세요.",
                    "blank": "내용을 입력해주세요.",
                }
            },
                        
        }
        
    def validate(self, attrs):
            title = attrs.get('title')
            content = attrs.get('content')
            meeting_city = attrs.get('meeting_city')
            place_title = attrs.get('place_title')
            place_address = attrs.get('place_address')
            
            cleaned_title = bleach.clean(title, tags=[], strip=True)
            cleaned_content = bleach.clean(content, tags=[], strip=True)
            cleaned_meeting_city = bleach.clean(meeting_city, tags=[], strip=True)
            cleaned_place_title = bleach.clean(place_title, tags=[], strip=True)
            cleaned_place_address = bleach.clean(place_address, tags=[], strip=True)

            attrs['title'] = cleaned_title
            attrs['content'] = cleaned_content
            attrs['meeting_city'] = cleaned_meeting_city
            attrs['place_title'] = cleaned_place_title
            attrs['place_address'] = cleaned_place_address
            
            images = self.context['request'].FILES.getlist("image")
            max_size = 1048576  # 1MB
            for image in images:
                img = Image.open(image)
                if image.size > max_size:
                    raise serializers.ValidationError("이미지 크기는 1MB를 초과할 수 없습니다.")


            return attrs
    
    

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.meeting_city = validated_data.get('meeting_city', instance.meeting_city)
        instance.meeting_at = validated_data.get('meeting_at', instance.meeting_at)
        instance.num_person_meeting = validated_data.get('num_person_meeting', instance.num_person_meeting)
        instance.meeting_status = validated_data.get('meeting_status', instance.meeting_status)
        instance.place_title = validated_data.get('place_title', instance.place_title)
        instance.place_address = validated_data.get('place_address', instance.place_address)

        instance.save()
        
        image_set = self.context['request'].FILES
        for image_data in image_set.getlist('image'):
            MeetingImage.objects.create(meeting=instance, image=image_data)
        return instance
    
        

'''모임 글 상세'''
class MeetingDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y.%m.%d %H:%M")
    updated_at = serializers.DateTimeField(format="%Y.%m.%d %H:%M")
    comment = MeetingCommentListSerializer(many=True) # 댓글 Nested Serializer
    meeting_image = MeetingImageSerializer(many=True, read_only=True)
    join_meeting_count = serializers.SerializerMethodField()
    join_meeting_user = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        return {"account": obj.user.account, "pk": obj.user.pk, "nickname": obj.user.nickname}

    def get_join_meeting_user(self, obj):
        return obj.join_meeting.all().values("id","nickname")
    
    def get_join_meeting_count(self, obj):
        return obj.join_meeting.count()
    
    class Meta:
        model = Meeting
        fields = "__all__"

'''모임 글 리스트, 작성, 상세, 수정 끝'''

'''모임 댓글 작성, 수정'''

'''모임 댓글 작성 수정'''
class MeetingCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingComment
        fields = ("content",)
        extra_kwargs = {
            
            "content": {
                "error_messages": {
                    "required": "내용을 입력해주세요.",
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
    

'''모임 댓글 작성, 수정 끝'''

'''모임 대댓글 목록, 작성, 수정 시작'''
class MeetingCommentReplyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingCommentReply
        fields = "__all__"

'''모임 대댓글 작성 수정'''
class MeetingCommentReplyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingCommentReply
        fields = ("content",)
        extra_kwargs = {
            
            "content": {
                "error_messages": {
                    "required": "내용을 입력해주세요.",
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

'''모임 대댓글 작성, 수정 끝'''

class MeetingStatusupdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ("meeting_status",)