
from django.contrib import admin
from django.urls import path, include
from biblioteca import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('biblioteca.urls')),
    path('api/', include('biblioteca.urls_api')),
]
