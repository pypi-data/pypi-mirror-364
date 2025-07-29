from django.contrib import admin
from django.urls import path
from django_basic_app.views import description

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', description, name='description'),  # root path
    path('demo/', description, name='demo'),    # add this to handle /demo/
]
