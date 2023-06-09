from meeting.models import (
    Meeting,
    MeetingComment,
    MettingCommentReply,
    )

from meeting.serializer import (
    MeetingListSerializer,
    MeetingCreateSerializer,
    MeetingDetailSerializer,
    MeetingCommentCreateSerializer,
    MeetingCommentReplyCreateSerializer,
    )

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404


# ================================ 모임 글 리스트, 작성, 상세, 수정, 삭제, 북마크 시작 ================================


class MeetingView(APIView):
    
    # 모임 글 리스트
    def get(self, request):
        meeting = Meeting.objects.all()
        serializer = MeetingListSerializer(meeting, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    #모임 글 작성
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"message":"로그인 해주세요"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = MeetingCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MeetingDetialView(APIView):

    #모임 글 상세 보기
    def get(self, request, meeting_id):
        meeting = get_object_or_404(Meeting, id=meeting_id)
        serializer = MeetingDetailSerializer(meeting)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    #모임 글 수정하기
    def patch(self, request, meeting_id):
        meeting = get_object_or_404(Meeting, id=meeting_id)
        if request.user == meeting.user:
            serializer = MeetingCreateSerializer(meeting, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
    #모임 글 삭제하기
    def delete(self, request, meeting_id):
        meeting = get_object_or_404(Meeting, id=meeting_id)
        if request.user == meeting.user:
            meeting.delete()
            return Response({"message":"삭제 완료"}, status=status.HTTP_204_NO_CONTENT)     
        else:
            return Response({"message":"권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

class MeetingBookmarkView(APIView):
    
    #모임 글 북마크하기
    def post(self, request, meeting_id):
        meeting = get_object_or_404(Meeting, id=meeting_id)
        if request.user in meeting.bookmark.all():
            meeting.bookmark.remove(request.user)
            return Response('북마크 취소', status=status.HTTP_200_OK)
        else:
            meeting.bookmark.add(request.user)
            return Response('북마크', status=status.HTTP_200_OK)
        
# ================================ 모임 글 리스트, 작성, 상세, 수정, 삭제, 북마크 끝 ================================

# ================================ 모임 댓글 작성, 수정, 삭제 시작 ================================

class MeetingCommentView(APIView):
    
    #모임 댓글 작성하기
    def post(self, request, meeting_id):
        serializer = MeetingCommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, meeting_id=meeting_id)
            return Response({"meesage":"작성완료"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class MeetingCommentDetailView(APIView):
    
    #모임 댓글 수정
    def put(self, request, comment_id, meeting_id):
        comment = get_object_or_404(MeetingComment, id= comment_id)
        if request.user == comment.user:
            serializer = MeetingCommentCreateSerializer(comment, request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"meesage":"수정완료"}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"meesage":"권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
    
    #모임 댓글 삭제
    def delete(self, request, comment_id, meeting_id):
        comment = get_object_or_404(MeetingComment, id=comment_id)
        if request.user == comment.user:
            if comment.reply.all():
                serializer = MeetingCommentCreateSerializer(comment, {"content":"삭제된 댓글 입니다."})
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

# ================================ 모임 댓글 작성, 수정, 삭제 끝 ================================

# ================================ 모임 대댓글 작성, 수정, 삭제 시작 ================================


class MeetingCommentReplyView(APIView):
    
    #모임 대댓글 작성
    def post(self, request, comment_id, meeting_id):
        serializer = MeetingCommentReplyCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, meeting_id=meeting_id, comment_id=comment_id)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MeetingCommentReplyDetailView(APIView):
    
    #모임 대댓글 수정
    def put(self, request, comment_id, meeting_id, reply_id):
        reply = get_object_or_404(MettingCommentReply, id=reply_id)
        if request.user == reply.user:
            serializer = MeetingCommentReplyCreateSerializer(reply, request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
    
    #모임 대댓글 삭제
    def delete(self, request, comment_id, meeting_id, reply_id):
        reply = get_object_or_404(MettingCommentReply, id=reply_id)
        if request.user == reply.user:
            reply.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message":"권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

# ================================ 모임 대댓글 작성, 수정, 삭제 끝 ================================