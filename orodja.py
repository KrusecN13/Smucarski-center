import re
import csv
from urllib.request import urlopen
import os

def shrani(url, ime_datoteke):
    r = urlopen(url).read().decode()
    datoteka = open(ime_datoteke, 'w')
    datoteka.write(r)

def shrani_skakalca(id):
        for i in range(10):
            shrani('http://data.fis-ski.com/dynamic/athlete-biography.html?sector=JP&competitorid=29533&type=result&bt=prev&limit=100&bt=next&rec_start={stevilo}'.format(stevilo=i*100),'{ident}.{st}'.format(ident=id,st=str(i)))


def vsebina_datoteke(ime_datoteke):
    with open(ime_datoteke) as datoteka:
        vsebina=datoteka.read()
    return vsebina

vzorec_iskanja= re.compile(r"<tr><td class='..'>(?P<datum>.*)&nbsp;</td>\n<td class='..'><a href=.*raceid=(?P<id>.*\d).>(?P<mesto>.*)</a>.*\n.*ys.>(?P<drzava>.*)&.*\n.*>(?P<kategorija>.*)&nb.*\n.*>(?P<disciplina>.*)&nb.*\n.*>(?P<uvrstitev>\d*)&")
imena_polj=['kategorija','datum','uvrstitev','drzava','mesto','disciplina','id']
iskanje_skoki= re.compile(r"Noriaki</a>&nbsp;</td>\n.*\n.*\n.*sp;(?P<prvi_skok>.*)<.*\n.*\n.*sp;(?P<drugi_skok>.*)<")
imena_skoki=['id','prvi_skok','drugi_skok']


def zdruzi_strani():
        with open ('csv_Noriaki','w') as csv_dat:
            writer = csv.DictWriter(csv_dat,fieldnames=imena_polj)
            writer.writeheader()
            for j in range(8):
                for ujemanje in re.finditer(vzorec_iskanja,vsebina_datoteke('Noriaki{st}'.format(st=j))):
                     writer.writerow(ujemanje.groupdict())

def skoki_csv():
     with open('csv_Noriaki','r') as csv_dat:
            reader = csv.DictReader(csv_dat)
            with open('csv_Skoki','w') as csv_dat2:
                writer = csv.DictWriter(csv_dat2,fieldnames=imena_skoki)
                writer.writeheader()
                for row in reader:
                     for ujemanje in re.finditer(iskanje_skoki,vsebina_datoteke('{id}'.format(id=row['id']))):
                         dict=ujemanje.groupdict()
                         dict['id']=row['id']
                         writer.writerow(dict)







def strani_tekem():
        with open('csv_Noriaki','r') as csv_dat:
            reader = csv.DictReader(csv_dat)
            for row in reader:
                if not os.path.isfile(row['id']):
                        shrani('http://data.fis-ski.com/dynamic/results.html?sector=JP&raceid={raceid}'.format(raceid=row['id']), '{raceid}'.format(raceid=row['id']))


zdruzi_strani()
