from meeting.models import (
    Meeting,
    MeetingComment,
    MeetingCommentReply,
    )

from meeting.serializer import (
    MeetingListSerializer,
    MeetingCreateSerializer,
    MeetingDetailSerializer,
    MeetingCommentCreateSerializer,
    MeetingCommentReplyCreateSerializer,
    MeetingImage,
    MeetingUpdateSerializer,
    MeetingCommentListSerializer,
    MeetingCommentReplyListSerializer,
    MeetingCommentReply,
    MeetingStatusupdateSerializer,
    )


from rest_framework import status, generics
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404



""" 모임 글 리스트, 작성, 상세, 수정, 삭제, 북마크, 북마크 한 글 시작 """

class MeetingView(APIView):
    
    ''' 모임 글 리스트'''
    def get(self, request):
        meeting = Meeting.objects.all().order_by("-created_at")
        serializer = MeetingListSerializer(meeting, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    '''모임 글 작성'''
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"message":"로그인 해주세요"}, status=status.HTTP_403_FORBIDDEN)
        serializer = MeetingCreateSerializer(data=request.data, context = {"request":request})
        if serializer.is_valid():
            serializer.save(user=request.user)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"meesage":"작성 실패"}, status=status.HTTP_400_BAD_REQUEST)

class MeetingDetialView(APIView):

    '''모임 글 상세 보기'''
    def get(self, request, meeting_id):
        meeting = get_object_or_404(Meeting, id=meeting_id)
        serializer = MeetingDetailSerializer(meeting)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    '''모임 글 수정하기'''
    def patch(self, request, meeting_id):
        if not request.user.is_authenticated:
            return Response({"message":"로그인 해주세요"}, status=status.HTTP_403_FORBIDDEN)
        meeting = get_object_or_404(Meeting, id=meeting_id)
        if request.user == meeting.user:
            serializer = MeetingUpdateSerializer(meeting, data=request.data, context = {"request":request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"meesage":"입력 해주세요"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
    '''모임 글 삭제하기'''
    def delete(self, request, meeting_id):
        if not request.user.is_authenticated:
            return Response({"message":"로그인 해주세요"}, status=status.HTTP_403_FORBIDDEN)
        meeting = get_object_or_404(Meeting, id=meeting_id)
        if request.user == meeting.user:
            meeting.delete()
            return Response({"message":"삭제 완료"}, status=status.HTTP_204_NO_CONTENT)     
        else:
            return Response({"message":"권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

class MeetingBookmarkView(APIView):
    
    '''모임 글 북마크하기'''
    def post(self, request, meeting_id):
        if not request.user.is_authenticated:
            return Response({"message":"로그인 해주세요"}, status=status.HTTP_403_FORBIDDEN)
        meeting = get_object_or_404(Meeting, id=meeting_id)
        if request.user in meeting.bookmark.all():
            meeting.bookmark.remove(request.user)
            return Response('북마크 취소', status=status.HTTP_200_OK)
        else:
            meeting.bookmark.add(request.user)
            return Response('북마크', status=status.HTTP_202_ACCEPTED)
        
    '''북마크한 모임 글 보기'''
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"message":"로그인 해주세요"}, status=status.HTTP_403_FORBIDDEN)
        user = request.user
        meeting = user.bookmark_meeting.all().order_by("-created_at")
        serializer = MeetingListSerializer(meeting, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
""" 모임 글 리스트, 작성, 상세, 수정, 삭제, 북마크, 북마크 한 글 끝 """

""" 모임 댓글 목록, 작성, 수정, 삭제 시작 """

class MeetingCommentView(APIView):
    '''모임 댓글 목록'''
    def get(self, request, meeting_id):
        comment = MeetingComment.objects.all()
        serializer = MeetingCommentListSerializer(comment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    '''모임 댓글 작성하기'''
    def post(self, request, meeting_id):
        if not request.user.is_authenticated:
            return Response({"message":"로그인 해주세요"}, status=status.HTTP_403_FORBIDDEN)
        serializer = MeetingCommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, meeting_id=meeting_id)
            return Response({"meesage":"작성완료"}, status=status.HTTP_200_OK)
        else:
            return Response({"meesage":"빈간을 입력해주세요"}, status=status.HTTP_400_BAD_REQUEST)
        
class MeetingCommentDetailView(APIView):
    
    '''모임 댓글 수정'''
    def put(self, request, comment_id, meeting_id):
        if not request.user.is_authenticated:
            return Response({"message":"로그인 해주세요"}, status=status.HTTP_403_FORBIDDEN)
        comment = get_object_or_404(MeetingComment, id= comment_id)
        if request.user == comment.user:
            serializer = MeetingCommentCreateSerializer(comment, request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"meesage":"수정완료"}, status=status.HTTP_200_OK)
            else:
                return Response({"meesage":"빈간을 입력해주세요"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"meesage":"권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
    
    '''모임 댓글 삭제'''
    def delete(self, request, comment_id, meeting_id):
        if not request.user.is_authenticated:
            return Response({"message":"로그인 해주세요"}, status=status.HTTP_403_FORBIDDEN)
        comment = get_object_or_404(MeetingComment, id=comment_id)
        if request.user == comment.user:
            if comment.reply.all():
                serializer = MeetingCommentCreateSerializer(comment, {"content":"삭제된 댓글 입니다."} )
                if serializer.is_valid():
                    serializer.save(content="삭제된 댓글 입니다.")
                    return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                comment.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message":"권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

""" 모임 댓글 작성, 수정, 삭제 끝 """

""" 모임 대댓글 목록, 작성, 수정, 삭제 시작 """

class MeetingCommentReplyView(APIView):

    '''모임 대댓글 목록'''
    def get(self, request, meeting_id, comment_id):
        reply = MeetingCommentReply.objects.all()
        serializer = MeetingCommentReplyListSerializer(reply, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    '''모임 대댓글 작성'''
    def post(self, request, comment_id, meeting_id):
        if not request.user.is_authenticated:
            return Response({"message":"로그인 해주세요"}, status=status.HTTP_403_FORBIDDEN)
        serializer = MeetingCommentReplyCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, meeting_id=meeting_id, comment_id=comment_id)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"meesage":"빈간을 입력해주세요"}, status=status.HTTP_400_BAD_REQUEST)

class MeetingCommentReplyDetailView(APIView):
    
    '''모임 대댓글 수정'''
    def put(self, request, meeting_id, reply_id):
        if not request.user.is_authenticated:
            return Response({"message":"로그인 해주세요"}, status=status.HTTP_403_FORBIDDEN)
        reply = get_object_or_404(MeetingCommentReply, id=reply_id)
        if request.user == reply.user:
            serializer = MeetingCommentReplyCreateSerializer(reply, request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"meesage":"빈간을 입력해주세요"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
    
    '''모임 대댓글 삭제'''
    def delete(self, request, meeting_id, reply_id):
        if not request.user.is_authenticated:
            return Response({"message":"로그인 해주세요"}, status=status.HTTP_403_FORBIDDEN)
        reply = get_object_or_404(MeetingCommentReply, id=reply_id)
        comment = reply.comment.content
        comments = reply.comment.reply.all()
        if request.user == reply.user:
            reply.delete()
            if comment == "삭제된 댓글 입니다.":
                if not comments:
                    reply.comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message":"권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
    
""" 모임 대댓글 작성, 수정, 삭제 끝 """

""" 모임 제목, 내용, 작성자 검색 기능 시작 """
class MeetingTitleSearchView(generics.ListAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title',]

class MeetingContentSearchView(generics.ListAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['content',]

class MeetingUserSearchView(generics.ListAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__nickname',]

class MeetingCitySearchView(generics.ListAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['meeting_city',]
'''모임 제목, 내용, 작성자 검색 기능 끝'''

""" 모임 이미지 삭제 시작 """
class MeetingImageDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, meeting_id, image_id):
        image = get_object_or_404(MeetingImage, id=image_id)
        meeting = get_object_or_404(Meeting, id=meeting_id)
        if request.user == meeting.user:
            image.delete()
            return Response({"message":"삭제 완료"}, status=status.HTTP_204_NO_CONTENT)     
        else:
            return Response({"message":"권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
""" 모임 이미지 삭제 끝 """

""" 유저가 작성한 모임 글 목록 시작 """
'''유저가 작성한 모임 글 목록 시작'''
class MyCreateMeetingView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"message":"로그인 해주세요"}, status=status.HTTP_403_FORBIDDEN)
        user = request.user
        meeting = user.my_meeting.all().order_by("-created_at")
        serializer = MeetingListSerializer(meeting, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

'''모임 글 모임 참가하기'''
class MeetingJoinMeetingView(APIView):

    def post(self, request, meeting_id):
        if not request.user.is_authenticated:
            return Response({"message":"로그인 해주세요"}, status=status.HTTP_403_FORBIDDEN)
        meeting = get_object_or_404(Meeting, id=meeting_id)
        num_person = meeting.num_person_meeting
        join_person = meeting.join_meeting.count()
        if request.user in meeting.join_meeting.all():
            meeting.join_meeting.remove(request.user)
            serializer = MeetingStatusupdateSerializer(meeting, {"meeting_status":"모집중"} )
            if serializer.is_valid():
                serializer.save(meeting_status="모집중")
            return Response({"message":"약속 취소"}, status=status.HTTP_200_OK)
        else:
            if int(num_person) == join_person:
                return Response({"message":"자리가 없습니다."}, status=status.HTTP_406_NOT_ACCEPTABLE)
            meeting.join_meeting.add(request.user)
            num_person = meeting.num_person_meeting
            join_person = meeting.join_meeting.count()
            if int(num_person) == join_person:
                serializer = MeetingStatusupdateSerializer(meeting, {"meeting_status":"자리없음"} )
                if serializer.is_valid():
                    serializer.save(meeting_status="자리없음")
            return Response({"message":"약속"}, status=status.HTTP_202_ACCEPTED)