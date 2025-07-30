from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from django.views.generic import TemplateView


urlpatterns = [
   path('admin/', admin.site.urls, name="admin"),
   path('', TemplateView.as_view(template_name="djprod.html")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
