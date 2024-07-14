# library_management/urls.py
from django.contrib import admin
from django.urls import path, include
from books.views import home  # Import the home view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),  # Home page
    path('admin/', admin.site.urls),
    path('books/', include('books.urls')),  # Include book URLs
    path('users/', include('users.urls')),  # Include user URLs
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
