from django.urls import path
from .views import ShortenURLView,redirect_to_original,ShortURLInfoView


urlpatterns = [
    path('shorten/', ShortenURLView.as_view(), name='shorten-url'),
    path('info/<str:short_id>/', ShortURLInfoView.as_view(), name='url-info'),
    path('<str:short_id>/', redirect_to_original, name='redirect'),
]
