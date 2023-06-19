from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import(
    Counsel,
    CounselComment,
    CounselReply,
    )

from .serializers import(
    CounselListSerializer,
    CounselCreateSerializer,
    CounselDetailSerializer,
    CounselCommentSerializer,
    CounselCommentCreateSerializer,
    CounselReplySerializer,
    CounselReplyCreateSerializer,
)


# ================================ 게시글 시작 ================================ 

class CounselView(APIView):
    # 글목록
    def get(self, request):
        counsels = Counsel.objects.all()
        serializer = CounselListSerializer(counsels, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 글작성
    def post(self, request):
        serializer = CounselCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CounselDetailView(APIView):
    # 글상세
    def get(self, request, counsel_id):
        counsel = get_object_or_404(Counsel, id=counsel_id)
        counsel_serializer = CounselDetailSerializer(counsel)
        return Response({'counsel':counsel_serializer.data}, status=status.HTTP_200_OK)
    
    # 글수정
    def put(self, request, counsel_id):
        counsel = get_object_or_404(Counsel, id=counsel_id)
        if counsel.user == request.user:
            serializer = CounselCreateSerializer(counsel, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"권한이 없습니다."}, status.HTTP_403_FORBIDDEN)
    # 글삭제
    def delete(self, request, counsel_id):
        counsel = get_object_or_404(Counsel, id=counsel_id)
        if counsel.user == request.user:
            counsel.delete()
            return Response({'message': '삭제 완료'},status=status.HTTP_200_OK)
        else:
            return Response({"message":"권한이 없습니다."}, status.HTTP_403_FORBIDDEN)
            
# 게시글 좋아요
class CounselLikeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, counsel_id):
        counsel = get_object_or_404(Counsel, id=counsel_id)
        if request.user in counsel.like.all():
            counsel.like.remove(request.user)
            return Response('좋아요 취소', status=status.HTTP_200_OK)
        else:
            counsel.like.add(request.user)
            return Response('좋아요', status=status.HTTP_202_ACCEPTED)

# ================================ 게시글 끝 ================================ 

# ================================ 댓글 시작 ================================ 

class CounselCommentView(APIView):
    # 댓글리스트
    def get(self, request, counsel_id):
        counsel = get_object_or_404(Counsel, id=counsel_id)
        comments = counsel.counsel_comment_counsel.all()
        serializer = CounselCommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # 댓글작성
    def post(self, request, counsel_id):
        serializer = CounselCommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, counsel_id=counsel_id)
            return Response({"meesage":"작성완료"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class CounselCommentDetailView(APIView):
    # 댓글수정
    def put(self, request, counsel_id, counsel_comment_id):
        comment = get_object_or_404(CounselComment, id=counsel_comment_id)
        if comment.user == request.user:
            serializer = CounselCreateSerializer(comment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"meesage":"수정완료"}, status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"권한이 없습니다."}, status.HTTP_403_FORBIDDEN)

    # 댓글삭제    
    def delete(self, request, counsel_id, counsel_comment_id):
        comment = get_object_or_404(CounselComment, id=counsel_comment_id)
        if request.user == comment.user:
            comment.delete()
            return Response({'message': '삭제 완료'},status=status.HTTP_200_OK)
        else:
            return Response({"message":"권한이 없습니다."}, status.HTTP_403_FORBIDDEN)


class CounselCommentLikelView(APIView):
    # 댓글 좋아요
    def post(self, request, counsel_id, counsel_comment_id):
        counselcomment = get_object_or_404(CounselComment, id=counsel_comment_id)
        if request.user in counselcomment.like.all():
            counselcomment.like.remove(request.user)
            return Response('댓글 좋아요 취소', status=status.HTTP_200_OK)
        else:
            counselcomment.like.add(request.user)
            return Response('댓글 좋아요', status=status.HTTP_202_ACCEPTED)
        
# ================================ 댓글 끝 ================================ 


# ================================ 대댓글 시작 ================================ 

class CounselReplyView(APIView):
    # 대댓글 리스트
    def get(self, request, counsel_id, counsel_comment_id):
        reply = CounselReply.objects.all()
        serializer = CounselReplySerializer(reply, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 대댓글 작성
    def post(self, request, counsel_id, counsel_comment_id):
        serializer = CounselReplyCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, counsel_id=counsel_id, comment_id=counsel_comment_id)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class CounselReplyDetailView(APIView):
    # 대댓글 수정
    def put(self, request, counsel_id, counsel_comment_id, counsel_reply_id):
        reply = get_object_or_404(CounselReply, id=counsel_reply_id)
        if request.user == reply.user:
            serializer = CounselReplyCreateSerializer(reply, request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
            
    # 대댓글 삭제
    def delete(self, request, counsel_id, counsel_comment_id, counsel_reply_id):
        reply = get_object_or_404(CounselReply, id=counsel_reply_id)
        if request.user == reply.user:
            reply.delete()
            return Response({"message":"삭제완료"},status=status.HTTP_200_OK)
        else:
            return Response({"message":"권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
    

class CounselReplyLikeView(APIView):
    permission_classes = [IsAuthenticated]
    # 대댓글 좋아요
    def post(self, request, counsel_id, counsel_comment_id, counsel_reply_id):
        counselcomment = get_object_or_404(CounselComment, id=counsel_comment_id)
        if request.user in counselcomment.like.all():
            counselcomment.like.remove(request.user)
            return Response('좋아요 취소', status=status.HTTP_200_OK)
        else:
            counselcomment.like.add(request.user)
            return Response('좋아요', status=status.HTTP_202_ACCEPTED)

# ================================ 대댓글 끝 ================================ 

