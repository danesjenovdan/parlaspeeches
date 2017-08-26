from django.shortcuts import render
from itertools import groupby
import re
from .models import *
import datetime

def parser():
	spl = []
	tab = []
	filename = "/home/t0mtom/Downloads/captions.srt"
	person = re.compile("^:[A-ZŽČŠĐĆ]*:")
	with open(filename) as f:
		res = [list(g) for b,g in groupby(f, lambda x: bool(x.strip())) if b]
		for spe in res:
			name_parser = (person.match(spe[2]))
			if name_parser is not None:
				np = name_parser.group().replace(':','')
				if Person.objects.filter(name_parser=np):
					print ("allready exists")
				else:
					per = Person(name_parser=np)
					per.save()
				if len(tab) != 0:
					if person.match(tab[0]).group().replace(':','') != np:
						spl = (spl[0])
						print (spl)
						speech = Speech(speaker=Person.objects.get(name_parser=spl['person']),
							   			content=''.join(spl['speeches']).replace(str(':'+spl['person']+':'), ''),
							   			start_time_stamp=spl['st'],
							   			end_time_stamp = toMS(spe[1], 1)
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
				

def toMS(t, st):
	spli = t.split(' --> ')
	t = spli[st].replace(',',":").split(':')
	seconds = (int(t[0]) * 3600) + (int(t[1]) * 60) + int(t[2]) + (int(t[3]) * float(0.001))
	return (seconds* 1000)