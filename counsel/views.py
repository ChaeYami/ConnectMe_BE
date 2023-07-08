from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination

from .models import (
    Counsel,
    CounselComment,
    CounselReply,
)


from .serializers import (
    CounselListSerializer,
    CounselCreateSerializer,
    CounselDetailSerializer,
    CounselCommentSerializer,
    CounselCommentCreateSerializer,
    CounselReplySerializer,
    CounselReplyCreateSerializer,
)
from django.db.models import F
from django.db.models import Count

"""페이지네이션 시작"""


class CounselPagination(PageNumberPagination):
    page_size = 15


"""페이지네이션 끝"""
"""게시글 시작"""


class CounselView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CounselPagination()

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAuthenticated(),
            ]
        else:
            return super(CounselView, self).get_permissions()

    """글목록"""

    def get(self, request):
        counsels = Counsel.objects.all().order_by("-id")
        paginator = self.pagination_class
        result_page = paginator.paginate_queryset(counsels, request)
        total_items = paginator.page.paginator.count
        serializer = CounselListSerializer(result_page, many=True)
        return Response(
            {"counsel": serializer.data, "total-page": total_items},
            status=status.HTTP_200_OK,
        )

    """글작성"""

    def post(self, request):
        serializer = CounselCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CounselDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "PUT" or self.request.method == "DELETE":
            return [
                IsAuthenticated(),
            ]
        else:
            return super(CounselDetailView, self).get_permissions()

    """글상세"""

    def get(self, request, counsel_id):
        counsel = get_object_or_404(Counsel, id=counsel_id)
        counsel_serializer = CounselDetailSerializer(counsel)
        return Response({"counsel": counsel_serializer.data}, status=status.HTTP_200_OK)

    """글수정"""

    def put(self, request, counsel_id):
        counsel = get_object_or_404(Counsel, id=counsel_id)
        if counsel.user == request.user:
            serializer = CounselCreateSerializer(
                counsel, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "권한이 없습니다."}, status.HTTP_403_FORBIDDEN)

    """글삭제"""

    def delete(self, request, counsel_id):
        counsel = get_object_or_404(Counsel, id=counsel_id)
        if counsel.user == request.user:
            counsel.delete()
            return Response({"message": "삭제 완료"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "권한이 없습니다."}, status.HTTP_403_FORBIDDEN)


"""작성한 게시글 모아보기"""


class MyCreateCounselView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CounselPagination

    def get(self, request):
        counsel = Counsel.objects.filter(user=request.user).order_by("-id")
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(counsel, request)
        total_items = paginator.page.paginator.count
        serializer = CounselListSerializer(result_page, many=True)
        return Response(
            {"counsel": serializer.data, "total-page": total_items}, status.HTTP_200_OK
        )


"""게시글 좋아요"""


class CounselLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, counsel_id):
        counsel = get_object_or_404(Counsel, id=counsel_id)
        if request.user in counsel.like.all():
            counsel.like.remove(request.user)
            counsel_like = counsel.like.count()
            return Response(
                {"message": "좋아요 취소", "counsel_like": counsel_like},
                status=status.HTTP_200_OK,
            )
        else:
            counsel.like.add(request.user)
            counsel_like = counsel.like.count()
            return Response(
                {"message": "좋아요", "counsel_like": counsel_like},
                status=status.HTTP_202_ACCEPTED,
            )


""" 게시글 끝 """

""" 댓글 시작 """


class CounselCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "PUT" or self.request.method == "DELETE":
            return [
                IsAuthenticated(),
            ]
        elif self.request.method == "POST":
            return [
                IsAuthenticated(),
            ]
        else:
            return super(CounselCommentView, self).get_permissions()

    """댓글리스트"""

    def get(self, request, counsel_id):
        counsel = get_object_or_404(Counsel, id=counsel_id)
        comments = counsel.counsel_comment_counsel.all()
        serializer = CounselCommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    """댓글작성"""

    def post(self, request, counsel_id):
        serializer = CounselCommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, counsel_id=counsel_id)
            return Response({"meesage": "작성완료"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CounselCommentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    """댓글수정"""

    def put(self, request, counsel_id, counsel_comment_id):
        comment = get_object_or_404(CounselComment, id=counsel_comment_id)
        if comment.user == request.user:
            serializer = CounselCommentSerializer(
                comment, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response({"meesage": "수정완료"}, status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "권한이 없습니다."}, status.HTTP_403_FORBIDDEN)

    """댓글삭제"""

    def delete(self, request, counsel_id, counsel_comment_id):
        comment = get_object_or_404(CounselComment, id=counsel_comment_id)
        if request.user == comment.user:
            if comment.reply.all():
                serializer = CounselReplyCreateSerializer(
                    comment, {"content": "삭제된 댓글 입니다."}
                )
                if serializer.is_valid():
                    serializer.save(content="삭제된 댓글 입니다.")
                    return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                comment.delete()
                return Response({"message": "삭제 완료"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)


class CounselCommentLikelView(APIView):
    permission_classes = [IsAuthenticated]

    """댓글 좋아요"""

    def post(self, request, counsel_id, counsel_comment_id):
        counselcomment = get_object_or_404(CounselComment, id=counsel_comment_id)
        if request.user in counselcomment.like.all():
            counselcomment.like.remove(request.user)
            comment_like = counselcomment.like.count()
            return Response(
                {"message": "댓글 좋아요 취소", "comment_like": comment_like},
                status=status.HTTP_200_OK,
            )
        else:
            counselcomment.like.add(request.user)
            comment_like = counselcomment.like.count()
            return Response(
                {"message": "댓글 좋아요", "comment_like": comment_like},
                status=status.HTTP_202_ACCEPTED,
            )


""" 댓글 끝 """


""" 대댓글 시작 """


class CounselReplyView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "PUT" or self.request.method == "DELETE":
            return [
                IsAuthenticated(),
            ]
        elif self.request.method == "POST":
            return [
                IsAuthenticated(),
            ]
        else:
            return super(CounselReplyView, self).get_permissions()

    """대댓글 리스트"""

    def get(self, request, counsel_id, counsel_comment_id):
        reply = CounselReply.objects.all()
        serializer = CounselReplySerializer(reply, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    """대댓글 작성"""

    def post(self, request, counsel_id, counsel_comment_id):
        serializer = CounselReplyCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                user=request.user, counsel_id=counsel_id, comment_id=counsel_comment_id
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CounselReplyDetailView(APIView):
    permission_classes = [IsAuthenticated]

    """대댓글 수정"""

    def put(self, request, counsel_id, counsel_reply_id):
        reply = get_object_or_404(CounselReply, id=counsel_reply_id)
        if request.user == reply.user:
            serializer = CounselReplyCreateSerializer(reply, request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "성공."}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

    """대댓글 삭제"""

    def delete(self, request, counsel_id, counsel_reply_id):
        reply = get_object_or_404(CounselReply, id=counsel_reply_id)
        if request.user == reply.user:
            reply.delete()
            return Response({"message": "삭제완료"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)


class CounselReplyLikeView(APIView):
    permission_classes = [IsAuthenticated]
    """대댓글 좋아요"""

    def post(self, request, counsel_id, counsel_reply_id):
        counselreply = get_object_or_404(CounselReply, id=counsel_reply_id)
        if request.user in counselreply.like.all():
            counselreply.like.remove(request.user)
            reply_like = counselreply.like.count()
            return Response(
                {"message": "좋아요 취소", "reply_like": reply_like},
                status=status.HTTP_200_OK,
            )
        else:
            counselreply.like.add(request.user)
            reply_like = counselreply.like.count()
            return Response(
                {"message": "좋아요", "reply_like": reply_like},
                status=status.HTTP_202_ACCEPTED,
            )


""" 대댓글 끝 """

""" 베스트 댓글 """
class TopCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, counsel_id):
        comments = CounselComment.objects.filter(counsel_id=counsel_id)

        comments_serializer = CounselCommentSerializer(comments, many=True)
        comments_data = comments_serializer.data

        for comment_data in comments_data:
            if comment_data.get("reply"):
                comment_data["reply"] = []

        replies = CounselReply.objects.filter(counsel_id=counsel_id)

        replies_serializer = CounselReplySerializer(replies, many=True)

        combined_data = []
        for i in range(max(len(comments), len(replies))):
            if i < len(comments):
                combined_data.append(comments_serializer.data[i])
            if i < len(replies):
                combined_data.append(replies_serializer.data[i])

        combined_data.sort(
            key=lambda x: x.get("comment_like_count", 0) + x.get("reply_like_count", 0),
            reverse=True,
        )
        combined_data = combined_data[:3]

        response_data = {"combined_data": combined_data}

        return Response(response_data, status=status.HTTP_200_OK)
