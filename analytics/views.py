# -*- coding: utf-8 -*-
from .models import Vote

from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count

# Create your views here.
def collect(request, type_):
    note = request.GET.get('note', '')
    Vote(type_of=type_, note=note).save()
    return JsonResponse({'status': 'added'})


def get_counter(request, type_):
    count = Vote.objects.filter(type_of=type_).count()
    return JsonResponse({'status': count})


def get_top(request, num):
    counters = Vote.objects.values('type_of').order_by('type_of').annotate(the_count=Count('type_of')).order_by('-the_count')
    return JsonResponse({'top': num,
                         'counters': [{'key': item['type_of'],
                                       'counter': item['the_count']}
                                        for item in counters[:int(num)]]})

