from django.shortcuts import render

from place.models import Place, PlaceComment, PlaceImage
from place.serializers import (
    PlaceCommentSerializer, 
    PlaceSerializer, 
    PlaceCreateSerializer, 
    PlaceCreateCommentSerializer, 
    PlaceUpdateSerializer, 
    PlaceDeleteCommentSerializer, 
    PlaceImageSerializer,
    PlaceDetailSerializer)

from user.models import User

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import get_object_or_404


# ================================ 장소 게시글 시작 ================================

class PlaceView(APIView):

    permission_classes = [IsAuthenticated]

    # 장소 추천 전체보기
    def get(self, request):
        place = Place.objects.all()
        serializer = PlaceSerializer(place, many=True)
        return Response(serializer.data)

    # 장소 추천 작성하기
    def post(self, request):  
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
    def get(self, request, place_id):  
        place = get_object_or_404(Place, id=place_id)
        query = place.place_comment_place.filter(main_comment=None).order_by('-updated_at')
        
        place_serializer = PlaceDetailSerializer(place).data
        comment_serializer = PlaceCommentSerializer(query, many=True).data

        return Response({'place':place_serializer, 'comment':comment_serializer})

    # 장소 추천 북마크
    def post(self, request, place_id):  
        user = request.user
        place = get_object_or_404(Place, id=place_id)

        if user in place.bookmark.all():
            place.bookmark.remove(user)
            return Response({"message":"북마크 취소"}, status.HTTP_200_OK)
        else:
            place.bookmark.add(user)
            return Response({"message":"북마크"}, status.HTTP_200_OK)

    # 장소 추천 수정하기
    def patch(self, request, place_id):  
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
    def delete(self, request, place_id):  
        login = request.user
        writer = get_object_or_404(Place, id=place_id)

        if login.is_staff:
            writer.delete()
            return Response(status.HTTP_200_OK)
        else:
            return Response({'message':'권한이 없습니다.'}, status.HTTP_403_FORBIDDEN)
        

class PlaceimageView(APIView):
    
    permission_classes = [IsAdminUser]
    
    # 이미지 가져오기
    # def get(self, request, place_id, place_image_id):
    #     place = PlaceImage.objects.filter(place=place_id)
    #     serializer = PlaceImageSerializer(place, many=True)
    #     return Response(serializer.data)
    
    # 이미지 추가하기
    def post(self, request, place_id, place_image_id):
        place = get_object_or_404(Place, id=place_id)
        for data in request.data.getlist('image'):
            PlaceImage.objects.create(place=place, image=data)
        return Response(status.HTTP_200_OK)
    
    # 이미지 수정하기
    def patch(self, request, place_id, place_image_id):
        place = get_object_or_404(Place, id=place_id)
        image_place = PlaceImage.objects.filter(place=place_id)
        image = get_object_or_404(PlaceImage, id=place_image_id)
        
        if image in image_place:
            image.delete()
            PlaceImage.objects.create(id=place_image_id, place=place, image=request.data['image'])
            return Response(status.HTTP_200_OK)
        else:
            return Response({'message':'존재하지 않는 이미지입니다.'}, status.HTTP_400_BAD_REQUEST)
    
    # 이미지 삭제하기
    def delete(self, request, place_id, place_image_id):
        image_place = PlaceImage.objects.filter(place=place_id)
        image = get_object_or_404(PlaceImage, id=place_image_id)
        
        if image in image_place:
            image.delete()
            return Response(status.HTTP_200_OK)
        else:
            return Response({'message':'존재하지 않는 이미지입니다.'}, status.HTTP_400_BAD_REQUEST)


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
        
        
# 북마크 장소 모아보기
class PlaceBookView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        book = user.place_bookmark.all()
        serializer = PlaceSerializer(book, many=True)
        return Response(serializer.data, status.HTTP_200_OK)
        


# ================================ 장소 게시글 종료 ================================

# ================================ 장소 댓글 시작 ================================


class PlaceCommentView(APIView):

    permission_classes = [IsAuthenticated]

    # (프론트) 해당 게시글 댓글 가져오기
    def get(self, request, place_id):  
        place = get_object_or_404(Place, id=place_id)
        # 대댓글을 중복으로 가져오지 않도록 최상위 댓글만 보여줌
        query = place.place_comment_place.filter(main_comment=None)
        serializer = PlaceCommentSerializer(query, many=True)
            
        return Response(serializer.data)
    
    # (최상위) 댓글 작성
    def post(self, request, place_id):  
        serializer = PlaceCreateCommentSerializer(data=request.data)
        place = get_object_or_404(Place, id=place_id)

        if serializer.is_valid():
            serializer.save(user=request.user, place=place)
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class PlaceCommentDetailView(APIView):

    permission_classes = [IsAuthenticated]
    
    # 대댓글 작성
    def post(self, request, place_id, place_comment_id):  
        upside_comment = get_object_or_404(PlaceComment, id=place_comment_id)
        place = get_object_or_404(Place, id=place_id)
        serializer = PlaceCreateCommentSerializer(data=request.data)
        if serializer.is_valid():
            # (상위 댓글을 가진 경우) 대댓글 이상 작성 금지
            if upside_comment.deep >= 1:
                return Response({'message':'대댓글에 댓글을 작성할 수 없습니다.'}, status.HTTP_403_FORBIDDEN)
            # (상위 댓글이 없는 경우) 대댓글
            else:
                serializer.save(user=request.user, place=place, main_comment=upside_comment, deep=upside_comment.deep+1)
                return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    # 댓글 수정
    def put(self, request, place_id, place_comment_id):
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
    def delete(self, request, place_id, place_comment_id):  
        login = request.user
        comment = PlaceComment.objects.filter(main_comment=place_comment_id)
        writer = get_object_or_404(PlaceComment, id=place_comment_id)
        place = get_object_or_404(Place, id=place_id)
        if writer in place.place_comment_place.all():
            if login == writer.user:
                serializer = PlaceDeleteCommentSerializer(writer, data=request.data)
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

