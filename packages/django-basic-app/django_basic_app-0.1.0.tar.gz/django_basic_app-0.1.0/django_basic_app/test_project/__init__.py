from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('demo/', include('django_basic_app.urls')),  # <- intègre ton app réutilisable ici
]
