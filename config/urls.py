from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from clientes import views as clientes_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("portal/gap/", clientes_views.gap, name="gap"),
    path("portal/roadmap/", clientes_views.roadmap, name="roadmap"),
    path("portal/calendario/", clientes_views.calendario, name="calendario"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
