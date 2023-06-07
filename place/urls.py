from django.urls import path
from place import views

urlpatterns = [
    path("", views.PlaceView.as_view(), name='place_view'),
    path("<int:place_id>", views.PlaceDetailView.as_view(),
         name='place_detail_view'),
    path("<int:place_id>/comment/", views.PlaceCommentView.as_view(),
         name='place_commment_view'),
    path("<int:place_id>/comment/<int:place_comment_id>/", views.PlaceCommentDetailView.as_view(),
         name='place_commment_detail_view'),
    path("<int:place_id>/comment/<int:place_comment_id>/reply/", views.PlaceReplyView.as_view(),
         name='place_reply_view'),
    path("<int:place_id>/comment/<int:place_comment_id>/reply/<int:place_reply_id>/", views.PlaceReplyDetailView.as_view(),
         name='place_reply_detail_view'),
]
