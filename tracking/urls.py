from django.urls import path
from . import views

urlpatterns = [
    path('', views.track_iss, name='track_iss'),
    path('', views.iss_form_view, name='iss-form'),
    path('api/track_iss/', views.track_iss_api, name='track_iss_api'),

]
