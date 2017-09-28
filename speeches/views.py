from itertools import groupby

from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import JsonResponse

from django.conf import settings
from django.http import JsonResponse

from .models import Speech, Person

import json
import requests
import re
import datetime
import pysolr


solr = pysolr.Solr(settings.SOLR_URL, timeout=10)

def index(request):
    return JsonResponse({"index": True})

def upload_srt(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        video_id = request.POST['video_id']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        parser(str(settings.MEDIA_ROOT+'/'+filename), str(filename), video_id)
        return redirect('/admin/speeches/speech/')
    return redirect('/admin/speeches/speech/')


def parser(filename, myfile, video_id):
    spl = []
    b = []
    tab = []
    tb = 0
    spe = ""
    speeches = Speech.objects.filter(video_id=video_id)
    if speeches:
        
        #print(solr.delete(q='video_id:'+str(video_id)))
        speeches.delete()

    person = re.compile("^:[A-ZŽČŠĐĆ]*:")
    with open(filename) as f:
        res = [list(g) for b,g in groupby(f, lambda x: bool(x.replace('\n', ''))) if b]
        for spe in res[1:]:
            b.append(spe[0])
            b.append(spe[1:])
            spe = b
            b = []
            spe[1] = ''.join(spe[1])
            name_parser = (person.match(spe[1].replace(' ','')))
            if name_parser is not None:
                np = name_parser.group().replace(':','')
                if len(Person.objects.filter(name_parser=np)) == 0:
                    per = Person(name_parser=np)
                    per.save()
                if len(tab) != 0:
                    if person.match(tab[0].replace(' ','')).group().replace(':','') != np:
                        spl = (spl[0])
                        con = ''.join(spl['speeches']).replace(str(':'+spl['person']+':'), '')
                        con = con.replace('\n', '')
                        speech = Speech(speaker=Person.objects.get(name_parser=spl['person']),
                                        content=con.lstrip(' '),
                                        start_time_stamp=spl['st'],
                                        end_time_stamp = tb,
                                        video_id = video_id)

                        speech.save()
                        spl = []
                        tab = []
                        tab.append(spe[1])
                        spl.append({'person': np,'speeches': tab, 'st': toMS(spe[0], 0), 'et': 0})
                else:
                    tab.append(spe[1])
                    spl.append({'person': np,'speeches': tab, 'st': toMS(spe[0], 0), 'et': 0})
            else:
                tab.append(spe[1])
                tb = toMS(spe[0], 1)
        spl = (spl[0])
        con = ''.join(spl['speeches']).replace(str(':'+spl['person']+':'), '')
        con = con.replace('\n', '')
        speech = Speech(speaker=Person.objects.get(name_parser=spl['person']),
                        content=con.lstrip(' '),
                        start_time_stamp=spl['st'],
                        end_time_stamp = tb,
                        video_id = video_id)

        speech.save()
        exportSpeeches(video_id)

def toMS(t, st):
    spli = t.split(' --> ')
    t = spli[st].replace('.',":").split(':')
    seconds = (float(t[0]) * 3600.0) + (float(t[1]) * 60.0) + float(t[2]) + (float(t[3]) * float(0.001))
    return (seconds* 1000)


def getSpeeches(request, video_id):
    data = []
    persons = Person.objects.all()
    p_data = {person.id: {'name': person.name,
                          'image_url': person.image.url if person.image else ''} for person in persons}
    speeches = Speech.objects.filter(video_id=str(video_id)).order_by('start_time_stamp')
    #print (speeches)
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

def exportSpeeches(video_id):
    speeches = Speech.objects.filter(video_id=video_id)

    i=0
    output = []
    for speech in speeches:
        output.append({
            'id': str(speech.id),
            'video_id': str(video_id),
            'speaker_name': str(speech.speaker.name) if speech.speaker.name else 'neki',
            'speaker_id': str(speech.speaker.id),
            'speaker_url': str(speech.speaker.image.url) if speech.speaker.image else '',
            'timestamp_start': str(speech.start_time_stamp),
            'timestamp_end': str(speech.end_time_stamp),
            'content_t': str(speech.content),
        })
    #print(output)
    solr.add(output)

    return 1


def search(request, video_id, words):
    results = solr.search(words, **{
        'df': 'content_t',
        'hl': 'true',
        'hl.fl': 'content_t',
        'hl.fragsize': '0',
        'fq': 'video_id:'+video_id
    })
    #print(vars(results))
    out = [result for result in results]
    for i, o in enumerate(out):
        out[i]['content_t'] = results.highlighting[out[i]['id']]['content_t'][0]
    return JsonResponse(out, safe=False)

def delete_all():
    solr.delete(q='*:*')
