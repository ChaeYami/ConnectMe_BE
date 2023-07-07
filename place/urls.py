from django.urls import path
from place import views

urlpatterns = [
    path("", views.PlaceView.as_view(), name='place_view'),
    path("<int:place_id>", views.PlaceDetailView.as_view(),
         name='place_detail_view'),
    path("<int:place_id>/like/", views.PlaceLikeView.as_view(),
         name='place_like_view'),
    path("<int:place_id>/comment/", views.PlaceCommentView.as_view(),
         name='place_comment_view'),
    path("<int:place_id>/comment/<int:place_comment_id>/", views.PlaceCommentDetailView.as_view(),
         name='place_comment_detail_view'),
    path("<int:place_id>/image/<int:place_image_id>/", views.PlaceImageView.as_view(),
         name='place_image_view'),
    
    # 쿼리셋을 가져와 리스트로 반환
    path("title/", views.PlaceTitleSearchView.as_view({'get': 'list'}), name="place_title_search_view"),
    path("region/", views.PlaceRegionSearchView.as_view({'get': 'list'}), name="place_region_search_view"),
    path("category/", views.PlaceCategoryView.as_view({'get': 'list'}), name="place_category_view"),
    
]
