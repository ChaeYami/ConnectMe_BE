from rest_framework import serializers
import urllib.parse

from meeting.models import (
    Meeting,
    MeetingComment,
    MeetingCommentReply,
    MeetingImage,
    )

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
    created_at = serializers.DateTimeField(format="%Y/%m/%d %H:%M")
    updated_at = serializers.DateTimeField(format="%Y/%m/%d %H:%M")
    user = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        return {"account": obj.user.account, "pk": obj.user.pk, "nickname": obj.user.nickname}
    
    class Meta:
        model = MeetingCommentReply
        fields = "__all__"

'''모임 댓글 리스트'''
class MeetingCommentListSerializer(serializers.ModelSerializer):
    reply = MeetingCommentReplyListSerializer(many=True) # 대댓글 Nested Serializer
    created_at = serializers.DateTimeField(format="%Y/%m/%d %H:%M")
    updated_at = serializers.DateTimeField(format="%Y/%m/%d %H:%M")
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
        fields = ("id","place","title","content","meeting_image","meeting_city","meeting_at","num_person_meeting","meeting_status","place_title","place_address",)

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
        fields = ("title","content","meeting_city","meeting_at","num_person_meeting","meeting_status","place_title","place_address",)

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
    created_at = serializers.DateTimeField(format="%Y/%m/%d %H:%M")
    updated_at = serializers.DateTimeField(format="%Y/%m/%d %H:%M")
    comment = MeetingCommentListSerializer(many=True) # 댓글 Nested Serializer
    meeting_image = MeetingImageSerializer(many=True, read_only=True)
    join_meeting_count = serializers.SerializerMethodField()
    join_meeting = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        return {"account": obj.user.account, "pk": obj.user.pk, "nickname": obj.user.nickname}

    def get_join_meeting(self, obj):
        return obj.join_meeting.all().values()
    
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

'''모임 대댓글 작성, 수정 끝'''

class MeetingStatusupdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ("meeting_status",)