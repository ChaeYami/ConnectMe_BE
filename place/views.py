from django.shortcuts import render

from place.models import Place, PlaceComment
from place.serializers import PlaceCommentSerializer, PlaceSerializer, PlaceCreateSerializer, PlaceCreateCommentSerializer, PlaceUpdateSerializer, PlaceDeleteCommentSerializer

from user.models import User

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404


# ================================ 장소 게시글 시작 ================================
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
        if request.user.is_staff:
            serializer = PlaceCreateSerializer(
                data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'권한이 없습니다.'}, status.HTTP_403_FORBIDDEN)


class PlaceDetailView(APIView):

    permission_classes = [IsAuthenticated]

    # 장소 추천 상세보기
    def get(self, request, place_id):  # ✔️
        place = get_object_or_404(Place, id=place_id)
        query = place.place_comment_place.filter(main_comment=None)
        
        place_serializer = PlaceSerializer(place).data
        comment_serializer = PlaceCommentSerializer(query, many=True).data

        return Response({'place':place_serializer, 'comment':comment_serializer})

    # 장소 추천 북마크
    def post(self, request, place_id):  # ✔️
        user = request.user
        place = get_object_or_404(Place, id=place_id)

        if user in place.bookmark.all():
            place.bookmark.remove(user)
            return Response({"message":"북마크 취소"}, status.HTTP_200_OK)
        else:
            place.bookmark.add(user)
            return Response({"message":"북마크"}, status.HTTP_200_OK)

    # 장소 추천 수정하기
    def patch(self, request, place_id):  # ✔️
        place = get_object_or_404(Place, id=place_id)

        if request.user.is_staff:
            serializer = PlaceUpdateSerializer(place, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'권한이 없습니다.'}, status.HTTP_403_FORBIDDEN)

    # 장소 추천 삭제하기
    def delete(self, request, place_id):  # ✔️
        login = request.user
        writer = get_object_or_404(Place, id=place_id)

        if login.is_staff:
            writer.delete()
            return Response(status.HTTP_200_OK)
        else:
            return Response({'message':'권한이 없습니다.'}, status.HTTP_403_FORBIDDEN)


# 장소 추천 좋아요
class PlaceLikeView(APIView):
    def post(self, request, place_id):
        place = get_object_or_404(Place, id=place_id)
        if request.user in place.like.all():
            place.like.remove(request.user)
            return Response({"message":"좋아요 취소"}, status.HTTP_200_OK)
        else:
            place.like.add(request.user)
            return Response({"message":"좋아요"}, status.HTTP_200_OK)


# ================================ 장소 게시글 종료 ================================

# ================================ 장소 댓글 시작 ================================


class PlaceCommentView(APIView):

    permission_classes = [IsAuthenticated]

    # (프론트) 해당 게시글 댓글 가져오기
    def get(self, request, place_id):  # ✔️
        place = get_object_or_404(Place, id=place_id)
        
        query = place.place_comment_place.filter(main_comment=None)
        serializer = PlaceCommentSerializer(query, many=True)
            
        return Response(serializer.data)

    # 댓글 작성
    def post(self, request, place_id):  # ✔️
        serializer = PlaceCreateCommentSerializer(data=request.data)
        place = get_object_or_404(Place, id=place_id)

        if serializer.is_valid():
            serializer.save(user=request.user, place=place)
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class PlaceCommentDetailView(APIView):

    permission_classes = [IsAuthenticated]

    # 댓글 수정
    def put(self, request, place_id, place_comment_id):  # ✔️
        comment = get_object_or_404(PlaceComment, id=place_comment_id)
        if request.user == comment.user:
            serializer = PlaceCreateCommentSerializer(
                comment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'권한이 없습니다.'}, status.HTTP_403_FORBIDDEN)

    # 댓글 삭제
    def delete(self, request, place_id, place_comment_id):  # ✔️
        login = request.user
        comment = PlaceComment.objects.filter(main_comment=place_comment_id)
        writer = get_object_or_404(PlaceComment, id=place_comment_id)
        if login == writer.user:
            serializer = PlaceDeleteCommentSerializer(
                writer, data=request.data)
            if serializer.is_valid():
                if comment:
                    serializer.save(content=None)
                    return Response(serializer.data, status.HTTP_200_OK)
                else:
                    writer.delete()
                    return Response(status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'권한이 없습니다.'}, status.HTTP_403_FORBIDDEN)


# ================================ 장소 댓글 종료 ================================

