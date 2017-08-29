from itertools import groupby

from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import JsonResponse

from parlaspeeches.settings import MEDIA_ROOT
from django.http import JsonResponse

from .models import Speech, Person

import json
import requests
import re
import datetime


SOLR_URL = 'http://localhost:8983/solr/parlaspeeches'


def upload_srt(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        video_id = request.POST['video_id']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        parser(str(MEDIA_ROOT+'/'+filename), str(filename), video_id)
        return redirect('/admin/speeches/speech/')
    return redirect('/admin/speeches/speech/')


def parser(filename, myfile, video_id):
    spl = []
    tab = []
    tb = 0
    if len(Speech.objects.filter(video_id=video_id)) == 0:
        person = re.compile("^:[A-ZŽČŠĐĆ]*:")
        with open(filename) as f:
            res = [list(g) for b,g in groupby(f, lambda x: bool(x.strip())) if b]
            for spe in res:
                print (spe)
                name_parser = (person.match(spe[2]))
                if name_parser is not None:
                    np = name_parser.group().replace(':','')
                    if len(Person.objects.filter(name_parser=np)) == 0:
                        per = Person(name_parser=np)
                        per.save()
                    if len(tab) != 0:
                        print (person.match(tab[0]).group().replace(':',''))
                        print (np)
                        if person.match(tab[0]).group().replace(':','') != np:
                            spl = (spl[0])
                            speech = Speech(speaker=Person.objects.get(name_parser=spl['person']),
                                            content=''.join(spl['speeches']).replace(str(':'+spl['person']+':'), ''),
                                            start_time_stamp=spl['st'],
                                            end_time_stamp = tb,
                                            video_id = video_id
                                )
                            speech.save()
                            spl = []
                            tab = []
                            tab.append(spe[2])
                            spl.append({'person': np,'speeches': tab, 'st': toMS(spe[1], 0), 'et': 0})
                    else:
                        tab.append(spe[2])
                        spl.append({'person': np,'speeches': tab, 'st': toMS(spe[1], 0), 'et': 0})
                else:
                    tab.append(spe[2])
                    tb = toMS(spe[1], 1)

            speech = Speech(speaker=Person.objects.get(name_parser=spl[0]['person']),
                content=''.join(spl[0]['speeches']).replace(str(':'+spl[0]['person']+':'), ''),
                start_time_stamp=spl[0]['st'],
                end_time_stamp = tb,
                video_id = video_id
                )
            speech.save()


def toMS(t, st):
    spli = t.split(' --> ')
    t = spli[st].replace(',',":").split(':')
    seconds = (int(t[0]) * 3600) + (int(t[1]) * 60) + int(t[2]) + (int(t[3]) * float(0.001))
    return (seconds* 1000)


def getSpeech(request, video_id):
    data = []
    persons = Person.objects.all()
    p_data = {person.id: {'name': person.name,
                          'image_url': person.gov_picture_url} for person in persons}
    speeches = Speech.objects.filter(video_id=str(video_id))
    print (speeches)
    for speech in speeches:
        sp_data = {'id': speech.id,
                   'content': speech.content,
                   'video_id': speech.video_id,
                   'start_time_stamp': speech.start_time_stamp,
                   'end_time_stamp': speech.end_time_stamp,
                   }
        sp_data.update(p_data[speech.speaker_id])
        data.append(sp_data)
    return JsonResponse(data, safe=False)


# SOLR STUFF


def exportSpeeches():
    speeches = Speech.objects.all()

    i=0
    for speech in speeches:
        output = [{
            'id': 'g' + str(speech.id),
            'speaker_name': speech.speaker.name,
            'speaker_i': speech.speaker.id,
            'timestamp_dt': speech.start_time_stamp,
            'content_t': speech.content,
            'tip_t': 'govor'
        }]

        output = json.dumps(output)

        if i % 100 == 0:
            url = SOLR_URL + '/update?commit=true'
            r = requests.post(url,
                              data=output,
                              headers={'Content-Type': 'application/json'})


        else:
            r = requests.post(SOLR_URL + '/update',
                              data=output,
                              headers={'Content-Type': 'application/json'})

        i = i + 1
    return 1


def search(request, words):
    rows = 50
    start_page = 0
    # solr_url = 'http://127.0.0.1:8983/solr/knedl/select?wt=json'
    solr_url = SOLR_URL + '/select?wt=json'

    q = words.replace('+', ' ')

    solr_params = {
        'q': 'content_t:' + q.replace('IN', 'AND').replace('!', '+'),
        'facet': 'true',
        'facet.range': 'datetime_dt',
        'facet.range.start': '2014-01-01T00:00:00.000Z',
        'facet.range.gap': '%2B1MONTHS',
        'facet.range.end': 'NOW',
        # 'sort': 'datetime_dt desc',
        'hl': 'true',
        'hl.fl': 'content_t',
        'hl.fragmenter': 'regex',
        'hl.regex.pattern': '\w[^\.!\?]{1,600}[\.!\?]',
        'hl.fragsize': '5000',
        'hl.mergeContiguous': 'false',
        'hl.snippets': '1',
        'fq': 'tip_t:govor',
        'rows': str(rows),
        'start': str(int(start_page) * rows) if start_page else '0',
    }

    # print q + 'asd'

    url = solr_url
    for key in solr_params:
        url = url + '&' + key + '=' + solr_params[key]

    # print url

    r = requests.get(url).json()
    return JsonResponse(r)