from django.shortcuts import render
from itertools import groupby
import re
from .models import *
import datetime
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from parlaspeeches.settings import MEDIA_ROOT
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

def upload_srt(request):
    print("Sejv fajla")
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        parser(str(MEDIA_ROOT+'/'+filename), str(filename))
        return redirect('/admin/speeches/speech/')
    return redirect('/admin/speeches/speech/')



def parser(filename, myfile):
	spl = []
	tab = []
	tb = 0
	if len(Speech.objects.filter(video_id=str(myfile))) == 0:
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
								   			video_id = myfile
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
	   			video_id = myfile
				)
			speech.save()


def toMS(t, st):
	spli = t.split(' --> ')
	t = spli[st].replace(',',":").split(':')
	seconds = (int(t[0]) * 3600) + (int(t[1]) * 60) + int(t[2]) + (int(t[3]) * float(0.001))
	return (seconds* 1000)


def getSpeech(request, video_id):
	data = []
	speeches = Speech.objects.filter(video_id=str(video_id))
	print (speeches)
	for speech in speeches:
		data.append({'name':speech.speaker.name,
					 'content': speech.content,
					 'video_id': speech.video_id,
					 'start_time_stamp': speech.start_time_stamp,
					 'end_time_stamp': speech.end_time_stamp

			}
			)
	return JsonResponse(data, safe=False)