from rest_framework import serializers
from .models import Place, PlaceComment, PlaceImage

BACKEND = 'http://127.0.0.1:8000'

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
    
    def get_image(self, obj):
        img = obj.place_image_place.first()
        if img:
            return {'id':img.id, 'url':BACKEND+img.image.url}
        else:
            return img
    
    class Meta:
        model = Place
        fields = ['id', 'user', 'title','category', 'address', 'score', 'price', 'hour', 'holiday', 'content', 'created_at', 'updated_at', 'image', 'bookmark', 'like']


# place 상세보기 시리얼라이저
class PlaceDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    def get_image(self, obj):
        images = obj.place_image_place.all()
        img = []
        for image in images:
            img.append({'id':image.id, 'url':BACKEND+image.image.url})
        return img
    
    class Meta:
        model = Place
        fields = ['id', 'user', 'title','category', 'address', 'score', 'price', 'hour', 'holiday', 'content', 'created_at', 'updated_at', 'image', 'bookmark', 'like']
        
        
# place 생성 시리얼라이저        
class PlaceCreateSerializer(serializers.ModelSerializer):
    image = PlaceImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Place
        exclude = ['user', 'bookmark', 'like']
        
    def create(self, validated_data):
        instance = Place.objects.create(**validated_data)
        image_set = self.context['request'].FILES
        for data in image_set.getlist("image"):
            PlaceImage.objects.create(place=instance, image=data)
        return instance


# place 수정 시리얼라이저    
class PlaceUpdateSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    CHOICES = [
            ('밥','밥'),
            ('술','술'),
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
    
    def get_image(self, obj):
        images = obj.place_image_place.all()
        img = []
        for image in images:
            img.append({'id':image.id, 'url':BACKEND+image.image.url})
        return img
    
    class Meta:
        model = Place
        exclude = ['user', 'bookmark', 'like']

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.category = validated_data.get('category', instance.category)
        instance.address = validated_data.get('address', instance.address)
        instance.score = validated_data.get('score', instance.score)
        instance.price = validated_data.get('price', instance.price)
        instance.hour = validated_data.get('hour', instance.hour)
        instance.holiday = validated_data.get('holiday', instance.holiday)
        instance.save()
        return instance
    
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
        # reply 전부 불러와서 updated_at을 최신순으로 정렬
        sorted_reply = sorted(instance.reply.all(), key=lambda x: x.updated_at, reverse=True)
        serializer = self.__class__(sorted_reply, many=True)
        serializer.bind('', self)
        return serializer.data
    
    def get_user_name(self, obj):
        user_name = obj.user.account
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