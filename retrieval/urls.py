from django.urls import path
from . import views, generate
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name="index"),
    path('retrieve/', views.retrieve, name="retrieve"),
    path('sentiment/', views.sentiment, name="sentiment"),
    path('autoc/', views.auto_complete, name="autocomplete"),
    path('gen/', views.gen_content, name="gen"),
    path('upl/', generate.upload_data, name="upl")
]