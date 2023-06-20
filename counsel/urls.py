from django.urls import path
from counsel import views


urlpatterns = [
    path('', views.CounselView.as_view(), name="counsel_view"), 
    path('<int:counsel_id>/', views.CounselDetailView.as_view(), name="counsel_detail_view"),

    path('<int:counsel_id>/like/', views.CounselLikeView.as_view(), name="counsel_like_view"),

    path('<int:counsel_id>/comment/', views.CounselCommentView.as_view(), name="counsel_comment_view"),
    path('<int:counsel_id>/comment/<int:counsel_comment_id>/', views.CounselCommentDetailView.as_view(), name="counsel_detail_comment_view"),
    path('<int:counsel_id>/comment/<int:counsel_comment_id>/like/', views.CounselCommentLikelView.as_view(), name="counsel_comment_like_view"),
    
    path('<int:counsel_id>/comment/<int:counsel_comment_id>/reply/', views.CounselReplyView.as_view(), name="counsel_reply_view"),
    path('<int:counsel_id>/comment/<int:counsel_comment_id>/reply/<int:counsel_reply_id>/', views.CounselReplyDetailView.as_view(), name="counsel_reply_detail_view"),
    path('<int:counsel_id>/comment/<int:counsel_comment_id>/reply/<int:counsel_reply_id>/like/', views.CounselReplyLikeView.as_view(), name="counsel_reply_like_view"),
]
