from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from TransPorto import views as transporto_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', transporto_views.index, name='home'),  # La raíz carga index.html
    path('TransPorto/', include('TransPorto.urls')),
    path('', include('TransPorto.urls')),

    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
