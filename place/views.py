from django.db.models import Count, Q

from place.models import Place, PlaceComment, PlaceImage
from place.serializers import (
    PlaceCommentSerializer, 
    PlaceSerializer, 
    PlaceCreateSerializer, 
    PlaceCreateCommentSerializer, 
    PlaceUpdateSerializer, 
    PlaceDeleteCommentSerializer,
    PlaceDetailSerializer)

from user.models import User, Profile

from rest_framework import viewsets
from rest_framework import status
from rest_framework import filters

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import get_object_or_404


"""페이지네이션 시작 """
   
class PlaceCategoryPagination(PageNumberPagination):
    page_size = 30
    
class PlaceBookPagination(PageNumberPagination):
    page_size = 10
    
"""페이지네이션 끝""" 


"""장소 게시글 시작""" 
class PlaceView(APIView):

    permission_classes = [IsAuthenticated]
    pagination_class = PlaceBookPagination()

    '''북마크 장소 모아보기'''
    def get(self, request):
        user = get_object_or_404(User, id=request.user.id)
        book = user.place_bookmark.all().order_by('-id')
        paginator = self.pagination_class
        result_page = paginator.paginate_queryset(book, request)
        total_items = paginator.page.paginator.count
        serializer = PlaceSerializer(result_page, many=True)
        return Response({"place": serializer.data, "total-page": total_items}, status=status.HTTP_200_OK)

    '''장소 추천 작성하기'''
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

    '''장소 추천 상세보기'''
    def get(self, request, place_id):  
        place = get_object_or_404(Place, id=place_id)
        query = place.place_comment_place.filter(main_comment=None)
        
        place_serializer = PlaceDetailSerializer(place).data
        comment_serializer = PlaceCommentSerializer(query, many=True).data

        return Response({'place':place_serializer, 'comment':comment_serializer})

    '''장소 추천 북마크'''
    def post(self, request, place_id):  
        user = request.user
        place = get_object_or_404(Place, id=place_id)

        if user in place.bookmark.all():
            place.bookmark.remove(user)
            bookmark_count = place.bookmark.count()
            return Response({"message":"북마크 취소", "book_count":bookmark_count}, status.HTTP_200_OK)
        else:
            place.bookmark.add(user)
            bookmark_count = place.bookmark.count()
            return Response({"message":"북마크", "book_count":bookmark_count}, status.HTTP_200_OK)

    '''장소 추천 수정하기'''
    def patch(self, request, place_id):  
        place = get_object_or_404(Place, id=place_id)

        if request.user.is_staff:
            serializer = PlaceUpdateSerializer(place, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'권한이 없습니다.'}, status.HTTP_403_FORBIDDEN)

    '''장소 추천 삭제하기'''
    def delete(self, request, place_id):  
        login = request.user
        writer = get_object_or_404(Place, id=place_id)

        if login.is_staff:
            writer.delete()
            return Response(status.HTTP_200_OK)
        else:
            return Response({'message':'권한이 없습니다.'}, status.HTTP_403_FORBIDDEN)
        

class PlaceImageView(APIView):
    
    permission_classes = [IsAdminUser]
    
    '''이미지 추가하기'''
    def post(self, request, place_id, place_image_id):
        place = get_object_or_404(Place, id=place_id)
        image_data_list = request.data.getlist('image')
        image_urls = []

        for index, data in enumerate(image_data_list, start=1):
            place_image = PlaceImage.objects.create(place=place, image=data)
            image_urls.append({'id': place_image.id, 'url': place_image.image.url})
        
        return Response(image_urls, status=status.HTTP_200_OK)
    
    '''이미지 삭제하기'''
    def delete(self, request, place_id, place_image_id):
        image_place = PlaceImage.objects.filter(place=place_id)
        image = get_object_or_404(PlaceImage, id=place_image_id)
        
        if image in image_place:
            image.delete()
            return Response(status.HTTP_200_OK)
        else:
            return Response({'message':'존재하지 않는 이미지입니다.'}, status.HTTP_400_BAD_REQUEST)


'''장소 추천 좋아요'''
class PlaceLikeView(APIView):
    def post(self, request, place_id):
        place = get_object_or_404(Place, id=place_id)
        
        if request.user in place.like.all():
            place.like.remove(request.user)
            like_count = place.like.count()
            return Response({"message":"좋아요 취소", "like_count":like_count}, status.HTTP_200_OK)
        else:
            place.like.add(request.user)
            like_count = place.like.count()
            return Response({"message":"좋아요", "like_count":like_count}, status.HTTP_200_OK)
    
        


""" 장소 게시글 종료 """


""" 장소 댓글 시작 """

class PlaceCommentView(APIView):

    permission_classes = [IsAuthenticated]

    '''(프론트) 해당 게시글 댓글 가져오기'''
    def get(self, request, place_id):  
        place = get_object_or_404(Place, id=place_id)
        # 대댓글을 중복으로 가져오지 않도록 최상위 댓글만 보여줌
        query = place.place_comment_place.filter(main_comment=None)
        serializer = PlaceCommentSerializer(query, many=True)
            
        return Response(serializer.data, status.HTTP_200_OK)
    
    '''(최상위) 댓글 작성'''
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
    
    '''단일 댓글 가져오기'''
    def get(self, request, place_id, place_comment_id):
        comment = get_object_or_404(PlaceComment, id=place_comment_id)
        serializer = PlaceCreateCommentSerializer(comment)
        if serializer.is_valid:
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    
    '''대댓글 작성'''
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

    '''댓글 수정'''
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

    '''댓글 삭제'''
    def delete(self, request, place_id, place_comment_id):  
        login = request.user
        comment = PlaceComment.objects.filter(main_comment=place_comment_id)
        writer = get_object_or_404(PlaceComment, id=place_comment_id)
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


""" 장소 댓글 종료 """


""" 장소 검색, 정렬 시작 """
# select, search 검색
class PlaceSearchView(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    pagination_class = PlaceCategoryPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['comment_count', 'like', 'bookmark', 'id',]
    ordering = ['-id']
    search_fields = ['title',]
    
    def get_queryset(self):
        # 댓글 수를 계산하여 comment_count 필드를 추가
        # annotate: 계산 후 새 필드를 추가
        queryset = super().get_queryset().annotate(comment_count=Count('place_comment_place'))
        category_query = self.request.query_params.get('category')
        
        if category_query is not None:
            queryset = queryset.filter(category__icontains=category_query)

        return queryset
    
    
'''카테고리 필터'''
class PlaceCategoryView(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    pagination_class = PlaceCategoryPagination
    ordering = ['-id']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['category',]
    
    def get_queryset(self):
        
        user = self.request.user
        
        if user.is_authenticated:
            try:
                # 로그인한 유저의 프로필 모델
                profile = Profile.objects.get(user=user)
                current_region1 = profile.current_region1
                current_region2 = profile.current_region2
                
                # 카테고리 선택시
                search_query = self.request.query_params.get('search')
                
                # 프로필.current_region이 address에 포함 되는지
                if current_region1 is not None and current_region2 is not None and search_query:
                    queryset = Place.objects.filter(Q(address__contains=current_region1) & Q(address__contains=current_region2))
                    queryset = queryset.filter(category__icontains=search_query)
                    
                    # current_region1,2에 검색 결과가 없으면 current1로 범위를 넓힘
                    if not queryset:
                        queryset = Place.objects.filter(address__startswith=current_region1)
                        queryset = queryset.filter(category__icontains=search_query)
                        
                    # 이것마저 없으면 전체 가져오기                        
                    if not queryset:
                        queryset = Place.objects.all()
                        queryset = queryset.filter(category__icontains=search_query)
                
                # 위치조회 거부시
                else:
                    queryset = Place.objects.all()
                    
            except Profile.DoesNotExist:
                queryset = Place.objects.all()
        else:
            queryset = Place.objects.all()

        return queryset
    
    
""" 장소 검색, 정렬 종료 """

