from django.conf.urls import include, url

from .views import collect, get_counter, get_top


urlpatterns = [
    url(r'^get/$', get_counter, name='get_counter'),
    url(r'^collect/(?P<type_>[ÖÜØÄÂÁÉÓÚÍÎöüøäâáéóúíîčćšžČĆŠŽa-zA-Z0-9 \-\+!"%\.,]+)', collect),
    url(r'^top/(?P<num>.+)', get_top),
    ]
