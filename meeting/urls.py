from meeting import views

from django.urls import path

urlpatterns = [
    path("",views.MeetingView.as_view(),), # /meeting/ 모임 글 작성, 목록
    path('<int:meeting_id>/',views.MeetingDetialView.as_view(),), # /meeting/<int:meeting_id>/ 모임 글 상세, 수정, 삭제
    path('<int:meeting_id>/bookmark/', views.MeetingBookmarkView.as_view(),), # /meeting/<int:meeting_id>/bookmark/ 모임 글 북마크
    path('<int:meeting_id>/comment/', views.MeetingCommentView.as_view(),), # /meeting/<int:meeting_id>/comment/ 모임 댓글 작성
    path('<int:meeting_id>/comment/<int:comment_id>/', views.MeetingCommentDetailView.as_view(),), # /meeting/<int:meeting_id>/comment/<int:comment_id>/ 모임 댓글 수정 삭제
    path('<int:meeting_id>/comment/<int:comment_id>/reply/', views.MeetingCommentReplyView.as_view(),), # /meeting/<int:meeting_id>/comment/<int:comment_id>/reply/ 모임 대댓글 작성
    path('<int:meeting_id>/comment/<int:comment_id>/reply/<int:reply_id>/', views.MeetingCommentReplyDetailView.as_view(),) # /meeting/<int:meeting_id>/comment/<int:comment_id>/reply/<int:reply_id>/ 모임 대댓글 수정 삭제 
]