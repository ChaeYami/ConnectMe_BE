from django.shortcuts import render

from place.models import Place, PlaceComment
from place.serializers import PlaceCommentSerializer, PlaceSerializer, PlaceCreateSerializer, PlaceCreateCommentSerializer
from user.models import User

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404

# postman 연결확인 ✔️


class PlaceView(APIView):

    permission_classes = [IsAuthenticated]

    # 장소 추천 전체보기
    def get(self, request):  # ✔️
        place = Place.objects.all()
        serializer = PlaceSerializer(place, many=True)
        return Response(serializer.data)

    # 장소 추천 작성하기
    def post(self, request):  # ✔️
        if request.user.is_admin:
            serializer = PlaceCreateSerializer(
                data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response('작성 성공')
            else:
                return Response({"message": f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('권한 없음')


class PlaceDetailView(APIView):

    permission_classes = [IsAuthenticated]

    # 장소 추천 상세보기
    def get(self, request, place_id):  # ✔️
        place = get_object_or_404(Place, id=place_id)
        serializer = PlaceSerializer(place)
        return Response(serializer.data)

    # 장소 추천 북마크
    def post(self, request, place_id):  # ✔️
        user = request.user
        place = get_object_or_404(Place, id=place_id)

        if user in place.bookmark.all():
            place.bookmark.remove(user)
            return Response('구취')
        else:
            place.bookmark.add(user)
            return Response('북맠')

    # 장소 추천 수정하기
    def patch(self, request, place_id):  # ✔️
        place = get_object_or_404(Place, id=place_id)

        # 일부만 수정가능하도록 수정해야함
        if request.user.is_admin:
            serializer = PlaceCreateSerializer(place, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response('place detail patch')
            else:
                return Response({"message": f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('권한 없음')

    # 장소 추천 삭제하기
    def delete(self, request, place_id):  # ✔️
        login = request.user
        writer = get_object_or_404(Place, id=place_id)

        if login.is_admin:
            writer.delete()
            return Response('place detail delete⭕')
        else:
            return Response('place detail delete❌')


class PlaceCommentView(APIView):
    # 댓글 가져오기 작성
    # 댓글 작성
    def post(self, request, place_id):
        serializer = PlaceCreateCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response('댓글작성⭕')
        else:
            return Response('댓글작성❌')


class PlaceCommentDetailView(APIView):
    # 댓글 수정
    def put(self, request, place_id, place_comment_id):
        return Response('댓글 수정')

    # 댓글 삭제
    def delete(self, request, place_id, place_comment_id):
        login = request.user
        writer = get_object_or_404(PlaceComment, id=place_comment_id)
        if login == writer.user:
            writer.delete()
            return Response('댓글 삭제⭕')
        else:
            return Response('댓글 삭제❌')


class PlaceReplyView(APIView):
    # 대댓글 작성
    # 대댓글 가져오기
    def post(self, request, place_id, place_comment_id):
        serializer = PlaceCreateCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response('댓글작성⭕')
        else:
            return Response('댓글작성❌')


class PlaceReplyDetailView(APIView):
    # 대댓글 수정
    def put(self, request, place_id, place_comment_id, place_reply_id):
        return Response('대댓글 수정')

    # 대댓글 삭제
    def delete(self, request, place_id, place_comment_id, place_reply_id):
        return Response('대댓글 삭제')
