from django.urls import path
from .views import show_page

urlpatterns = [
    path("", show_page, name="web_show_page"),
]