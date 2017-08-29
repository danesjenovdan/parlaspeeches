from django.conf.urls import include, url
from django.contrib.auth import views as auth_views

from .views import upload_srt, search, getSpeech


urlpatterns = [
    url(r'^upload_srt/$', upload_srt, name='upload_srt'),
    url(r'^getSpeech/(?P<video_id>.+)', getSpeech),
    url(r'^q/(?P<words>[ÖÜØÄÂÁÉÓÚÍÎöüøäâáéóúíîčćšžČĆŠŽa-zA-Z0-9 \-\+!"%\.,]+)', search),
    ]