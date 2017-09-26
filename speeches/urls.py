from django.conf.urls import include, url
from django.contrib.auth import views as auth_views

from .views import upload_srt, search, getSpeeches, index


urlpatterns = [
    url(r'^$', index, name='home'),
    url(r'^upload_srt/$', upload_srt, name='upload_srt'),
    url(r'^getSpeeches/(?P<video_id>.+)', getSpeeches),
    url(r'^q/(?P<video_id>.+)/(?P<words>[ÖÜØÄÂÁÉÓÚÍÎöüøäâáéóúíîčćšžČĆŠŽa-zA-Z0-9 \-\+!"%\.,]+)', search),
    ]
