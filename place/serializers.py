from rest_framework import serializers
from .models import Place, PlaceComment, PlaceImage

# place 이미지 시리얼라이저
class PlaceImageSerializer(serializers.ModelSerializer):
    # 이미지 url로 반환
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = PlaceImage
        fields = ["image", ]


# place 전체보기 시리얼라이저
class PlaceSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    def get_image(self, obj):
        image = obj.place_image_place.all()
        return PlaceImageSerializer(instance=image, many=True).data
    
    class Meta:
        model = Place
        fields = '__all__'
        
        
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

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance
    
    
# 댓글 출력을 위한 오버라이딩
class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, instance):
        serializer = self.parent.parent.__class__(instance, context=self.context)
        return serializer.data


# place 댓글 시리얼라이저
class PlaceCommentSerializer(serializers.ModelSerializer):
    reply = serializers.SerializerMethodField()
    # slug_field : Place 모델의 title
    place = serializers.SlugRelatedField(queryset=Place.objects.all(), slug_field='id')
    
    class Meta:
        model = PlaceComment
        fields = ['id', 'user', 'place', 'content', 'main_comment', 'created_at', 'updated_at', 'reply']
        
    def get_reply(self, instance):
        serializer = self.__class__(instance.reply, many=True)
        serializer.bind('', self)
        return serializer.data


# place 댓글 생성 시리얼라이저
class PlaceCreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceComment
        fields = ['content', 'main_comment']
