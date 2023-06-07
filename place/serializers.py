from rest_framework import serializers
from .models import Place, PlaceComment


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = '__all__'


class PlaceImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Place
        fields = ["image", ]


class PlaceCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Place
        exclude = ['user', 'bookmark']


class PlaceCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceComment
        fields = '__all__'


class PlaceCreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceComment
        fields = ['content', 'main_comment']
