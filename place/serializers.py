from rest_framework import serializers
from .models import Place, PlaceComment, PlaceImage
from .validators import score_validator

BACKEND = 'http://127.0.0.1:8000' # 로컬환경에서

# ================================ 이미지 시리얼라이저 시작 ================================
class PlaceImageSerializer(serializers.ModelSerializer):
    # 이미지 url로 반환
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = PlaceImage
        fields = ["id", "image"]
        
# ================================ 이미지 시리얼라이저 끝 ================================

# ================================ 게시글 시리얼라이저 시작 ================================

# place 전체보기 시리얼라이저
class PlaceSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    bookmark_count = serializers.SerializerMethodField()
    
    def get_image(self, obj):
        img = obj.place_image_place.first()
        if img:
            url = img.image.url
            if 'https' in url:
                return {'id':img.id, 'url':'https://'+url[16:]}
            else:
                return {'id':img.id, 'url':BACKEND+img.image.url} # 로컬환경에서
        else:
            return img
        
    def get_comment_count(self, obj):
        return obj.place_comment_place.count()
    
    def get_like_count(self, obj):
        return obj.like.count()
    
    def get_bookmark_count(self, obj):
        return obj.bookmark.count()
    
    class Meta:
        model = Place
        fields = ['id', 'user', 'title','category', 'sort', 'comment_count', 'like_count', 'bookmark_count', 'address', 'score', 'price', 'hour', 'holiday', 'content', 'created_at', 'updated_at', 'image', 'bookmark', 'like']


# place 상세보기 시리얼라이저
class PlaceDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    bookmark_count = serializers.SerializerMethodField()
    
    def get_image(self, obj):
        images = obj.place_image_place.all()
        img = []
        for image in images:
            url = image.image.url
            if 'https' in url:
                img.append({'id':image.id, 'url':'https://'+url[16:]})
            else:
                img.append({'id':image.id, 'url':BACKEND+image.image.url})
        return img
    
    def get_comment_count(self, obj):
        return obj.place_comment_place.count()
    
    def get_like_count(self, obj):
        return obj.like.count()
    
    def get_bookmark_count(self, obj):
        return obj.bookmark.count()
    
    class Meta:
        model = Place
        fields = ['id', 'user', 'title','category', 'sort', 'comment_count', 'like_count', 'bookmark_count', 'address', 'score', 'price', 'hour', 'holiday', 'content', 'created_at', 'updated_at', 'image', 'bookmark', 'like']
        
        
# place 생성 시리얼라이저        
class PlaceCreateSerializer(serializers.ModelSerializer):
    image = PlaceImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Place
        exclude = ['user', 'bookmark', 'like', 'created_at', 'updated_at']
        extra_kwargs = {
            "title": {
                "error_messages": {
                    "required": "제목은 필수 입력 사항입니다.",
                    "blank": "제목은 필수 입력 사항입니다.",
                }
            },
            "content" : {
                "error_messages" : {
                    "required" : "내용은 필수 입력 사항입니다.",
                    "blank" : "내용은 필수 입력 사항입니다."
                }
            },
            "category" : {
                "error_messages" : {
                    "required" : "카테고리는 필수 입력 사항입니다.",
                    "blank" : "카테고리는 필수 입력 사항입니다."
                }
            },
            "address" : {
                "error_messages" : {
                    "required" : "주소는 필수 입력 사항입니다.",
                    "blank" : "주소는 필수 입력 사항입니다."
                }
            },
            "score" : {
                "error_messages" : {
                    "required" : "별점은 필수 입력 사항입니다.",
                    "blank" : "별점은 필수 입력 사항입니다.",
                    "invalid": "별점은 0~5.0 이하의 숫자만 입력할 수 있습니다.",
                }
            },
            "price" : {
                "error_messages" : {
                    "required" : "가격은 필수 입력 사항입니다.",
                    "blank" : "가격은 필수 입력 사항입니다."
                }
            },
            "hour" : {
                "error_messages" : {
                    "required" : "영업시간은 필수 입력 사항입니다.",
                    "blank" : "영업시간은 필수 입력 사항입니다."
                }
            },
            "holiday" : {
                "error_messages" : {
                    "required" : "휴일은 필수 입력 사항입니다.",
                    "blank" : "휴일은 필수 입력 사항입니다."
                }
            },
            }
        
    def validate(self,data):
        score = data.get("score")
        
        if score_validator(score):
            raise serializers.ValidationError(
                detail={"score": "별점은 0~5.0 이하의 숫자만 입력할 수 있습니다."}
            )
        return data
        
    def create(self, validated_data):
        instance = Place.objects.create(**validated_data)
        image_set = self.context['request'].FILES
        for data in image_set.getlist("image"):
            PlaceImage.objects.create(place=instance, image=data)
        return instance


# place 수정 시리얼라이저    
class PlaceUpdateSerializer(serializers.ModelSerializer):

    CHOICES = [
            ('식사','식사'),
            ('주점','주점'),
            ('카페','카페'),
        ]
    title = serializers.CharField(required=False)
    content = serializers.CharField(required=False)
    category = serializers.ChoiceField(required=False, choices=CHOICES)
    address = serializers.CharField(required=False)
    score = serializers.FloatField(required=False)
    price = serializers.CharField(required=False)
    hour = serializers.CharField(required=False)
    holiday = serializers.CharField(required=False)
    
    class Meta:
        model = Place
        exclude = ['user', 'bookmark', 'like']
    
# ================================ 게시글 시리얼라이저 끝 ================================

# ================================ 댓글 시리얼라이저 시작 ================================
    
# 댓글 출력을 위한 오버라이딩
class RecursiveSerializer(serializers.Serializer):
    # 부모의 직렬화 인스턴스 생성
    def to_representation(self, instance):
        serializer = self.parent.parent.__class__(instance, context=self.context)
        return serializer.data


# place 댓글 시리얼라이저
class PlaceCommentSerializer(serializers.ModelSerializer):
    reply = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    # slug_field : Place 모델의 id
    # place = serializers.SlugRelatedField(queryset=Place.objects.all(), slug_field='id')
    
    class Meta:
        model = PlaceComment
        fields = ['id', 'user', 'user_name', 'place', 'content', 'main_comment', 'deep', 'created_at', 'updated_at', 'reply']
        
    def get_reply(self, instance):
        replies = instance.reply.all()
        serializer = self.__class__(replies, many=True)
        serializer.bind('', self)
        return serializer.data
    
    def get_user_name(self, obj):
        user_name = obj.user.account
        if obj.content == None:
            return '사용자'
        else:
            return user_name
    
    def get_content(self, obj):
        if obj.content == None:
            return '삭제된 댓글입니다.'
        else:
            return obj.content

# place 댓글 생성, 수정 시리얼라이저
class PlaceCreateCommentSerializer(serializers.ModelSerializer):
    content = serializers.CharField(allow_blank=False, allow_null=False)
    class Meta:
        model = PlaceComment
        fields = ['id', 'content']
        

# place 댓글 삭제 시리얼라이저
class PlaceDeleteCommentSerializer(serializers.ModelSerializer):
    content = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    class Meta:
        model = PlaceComment
        fields = ['content',]
        
    

# ================================ 댓글 시리얼라이저 끝 ================================