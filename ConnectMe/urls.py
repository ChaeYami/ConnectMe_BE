from django.contrib import admin

from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from counsel import views

#cunsel에서 볼 수 있는 화면 
#url 매핑
urlpatterns = [
    path("admin/", admin.site.urls),
    path("user/", include("user.urls")),
    path("place/", include("place.urls")),
    path("meeting/", include("meeting.urls")),
    path("chat/", include("chat.urls")),
    path('counsel/', include('counsel.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


