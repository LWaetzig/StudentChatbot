from django.contrib import admin
from django.urls import path
from django.conf import settings
from StudentGPT.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", index, name="home"),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
