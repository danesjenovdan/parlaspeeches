from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from .views import getSpeech
from .views import upload_srt

urlpatterns = [
    url(r'^upload_srt/$', upload_srt, name='upload_srt'),
    url(r'^getSpeech/(?P<video_id>.+)', getSpeech)
    ]