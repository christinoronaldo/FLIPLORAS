from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("ex",include("studio.urls")),
    path('api/',include("api.urls")),
]