from django.contrib import admin
from django.urls import path
from myapp import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', views.index),
    path('home/', views.index),
    path('', views.index),
    path('signup/', views.sign_up, name='signup'),
    path('login/', views.signin, name='signin'),
    path('DocumentUpload/', views.upload_file, name='upload_file'),
    path('api/upload/', views.upload_file, name='upload_file'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

