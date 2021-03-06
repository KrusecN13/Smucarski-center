import re
import csv
from urllib.request import urlopen
import os

def shrani(url, ime_datoteke):
    #shrani spletno stran
    if url !='' and ime_datoteke != '':
        r = urlopen(url).read().decode()
        datoteka = open(ime_datoteke, 'w')
        datoteka.write(r)


def vsebina_datoteke(ime_datoteke):
    #prebere datoteko
    with open(ime_datoteke) as datoteka:
        vsebina=datoteka.read()
    return vsebina



konec_strani=re.compile(r"results&nbsp;found")
tekmovalec_ime= re.compile(r"Athlete : (?P<ime>.*)<")
tekmovalec_info = re.compile(r"Birthdate.*\n.*>(?P<Rojstni_dan>.*)<.*\n.*\n.*\n.*\n.*\n(?P<Spol>\w*).*\n.*\n.*\n.*\n.*old..(?P<status>\w*).*\n.*\n.*\n.*\n.*\n.*ays..(?P<Drzava>...).*\n.*\n.*\n.*\n.*ld..(?P<klub>.*)<")
tekmovalec_info_polja=['ime','Rojstni_dan', 'Spol', 'status','Drzava','klub']



def najdi_id(ime,priimek):
    if ime != None and priimek != None:
        #za vsak slucaj preverimo da nismo dobili praznega iskanja
        stran = 'https://data.fis-ski.com/global-links/search-a-athlete.html?listid=&lastname={}&gender=ALL&sector=JP&firstname={}'.format(priimek,ime)
        #fis stran za iskanje 
        shrani(stran,ime+priimek)
        #shranimo stran
        tekmovalec_id = re.compile(r'competitorid=(?P<id>.*)">{}'.format(priimek.upper()))
        for ujemanje in re.finditer(tekmovalec_id,vsebina_datoteke(ime+priimek)):
            #poiscemo id
            os.remove(ime+priimek)
            return(ujemanje.groupdict()['id'])
        os.remove(ime+priimek)
        
def shrani_skakalca(id):
        
        if not os.path.isfile('tekmovalci/csv_{id}.txt'.format(id=id)):
            #ce slucajno obstaja je brezveze se enkrat shranjevat
            shrani('https://data.fis-ski.com/dynamic/athlete-biography.html?sector=JP&competitorid={id}'.format(id=id),'{id}'.format(id=id))
            with open ('tekmovalci/info_{id}'.format(id=id),'w') as datoteka:
                writer = csv.DictWriter(datoteka,fieldnames = tekmovalec_info_polja)
                writer.writeheader()
                for ujemanje in re.finditer(tekmovalec_info,vsebina_datoteke('{id}'.format(id=id))):
                    for ime in re.finditer(tekmovalec_ime,vsebina_datoteke('{id}'.format(id=id))):
                        dic=ujemanje.groupdict()
                        ime.groupdict()
                        dic['ime']=ime.groupdict()['ime']
                        writer.writerow(dic)
                os.remove('{id}'.format(id=id))
            nadaljujem = True
            i=0
            while nadaljujem:
                #shranjuje strani dokler imajo se rezultate tekem
                shrani('http://data.fis-ski.com/dynamic/athlete-biography.html?sector=JP&competitorid={ident}&type=result&bt=prev&limit=100&bt=next&rec_start={stevilo}'.format(ident=id,stevilo=i*100),'{ident}{st}.txt'.format(ident=id,st=str(i)))
                if re.search(konec_strani,vsebina_datoteke('{ident}{st}.txt'.format(ident=id,st=str(i))))!= None:
                    nadaljujem = False
                    os.remove('{ident}{st}.txt'.format(ident=id,st=str(i)))
                i=i+1
            zdruzi_strani(id)


vzorec_iskanja= re.compile(r"<tr><td class='..'>(?P<datum>.*)&nbsp;</td>\n<td class='..'><a href=.*raceid=(?P<id>.*\d).>(?P<mesto>.*)</a>.*\n.*ys.>(?P<drzava>.*)&.*\n.*>(?P<kategorija>.*)&nb.*\n.*>(?P<disciplina>.*)&nb.*\n.*>(?P<uvrstitev>\d*)&")
imena_polj=['kategorija','datum','uvrstitev','drzava','mesto','disciplina','id']
iskanje_skoki= re.compile(r"Noriaki</a>&nbsp;</td>\n.*\n.*\n.*sp;(?P<prvi_skok>.*)<.*\n.*\n.*sp;(?P<drugi_skok>.*)<")
imena_skoki=['id','prvi_skok','drugi_skok']

tekme=re.compile(r"sp;(?P<mesto>.*)</td>\n.*\n.*\n.*competitorid=(?P<id_tekmovalca>.*)&am.*</a>&nbsp;</td>\n.*\n.*\n.*sp;(?P<prvi_skok>.*)<.*\n.*sp;(?P<prvi_tocke>.*)<.*\n.*sp;(?P<drugi_skok>.*)<.*\n.*sp;(?P<drugi_tocke>.*)<.*\n.*sp;(?P<skupaj_tocke>.*)<.*")
imena_tekme=['mesto','id_tekmovalca','prvi_skok','prvi_tocke','drugi_skok','drugi_tocke', 'skupaj_tocke']
imena_tekme_novaverzija=['mesto','id_tekmovalca']


mestoRegex= re.compile(r"&nbsp;(?P<mesto>\d?\d?)<")

            
def zdruzi_strani(id):
    #zdruzi strani tekem v eno
    if not os.path.isfile('tekmovalci/csv_{id}.txt'.format(id=id)):
    
        with open ('tekmovalci/csv_{id}.txt'.format(id=id),'w') as csv_dat:
            writer = csv.DictWriter(csv_dat,fieldnames=imena_polj)
            writer.writeheader()
            j=0
            while os.path.isfile('{id}{st}.txt'.format(id=id,st=j)):
                #dokler obstajajo shranjene spletne strani
                for ujemanje in re.finditer(vzorec_iskanja,vsebina_datoteke('{id}{st}.txt'.format(id=id,st=j))):
                     writer.writerow(ujemanje.groupdict())
                os.remove('{id}{st}.txt'.format(id=id,st=j))
                j=j+1





def shrani_tekmo(id,id_tekmovalca=True):
    #ce ne dodamo id_tekmovalca, bomo shranili rezultate vseh tekmovalcev za to tekmo
    if not os.path.isfile('tekme/tekma_{id}.txt'.format(id=id)):
                        shrani('http://data.fis-ski.com/dynamic/results.html?sector=JP&raceid={raceid}'.format(raceid=id), '{raceid}'.format(raceid=id))
                        with open('tekme/tekma_{id}.txt'.format(id=id),'w') as csv_dat2:
                            writer = csv.DictWriter(csv_dat2,fieldnames=imena_tekme)
                            writer.writeheader()
                        
                            for ujemanje in re.finditer(tekme,vsebina_datoteke('{id}'.format(id=id))):
                                 dict=ujemanje.groupdict()
                                 if dict["id_tekmovalca"] == id_tekmovalca or id_tekmovalca==True:
                                     writer.writerow(dict)
                        os.remove(str(id))


def shrani_tekmo_novaverzija(id,id_tekmovalca):
    #se ena verzija podobne funkcije kot zgoraj, ta poisce mesto tekmovalca na tekmi
    #na zalost je tudi ta kar pocasna(kot so pac regexi :() tako da nevem kero uporabit
    if not os.path.isfile('tekme/tekma_{id}.txt'.format(id=id)):
                        shrani('http://data.fis-ski.com/dynamic/results.html?sector=JP&raceid={raceid}'.format(raceid=id), '{raceid}'.format(raceid=id))
                        with open('tekme/tekma_{id}.txt'.format(id=id),'w') as csv_dat2:
                            writer = csv.DictWriter(csv_dat2,fieldnames=imena_tekme)
                            writer.writeheader()
                            counter=0
                            regexTekmovalec = re.compile("competitorid={id}".format(id=id_tekmovalca))
                            with open('{id}'.format(id=id),'r') as datotekaTekma:
                                datotekaTekma=datotekaTekma.readlines()
                                gremoven=False
                                gremoven2=False
                                dict={}
                                dict['id_tekmovalca']=id_tekmovalca
                                for vrstica in datotekaTekma:
                                    for ujemanje in re.finditer(regexTekmovalec,vrstica):
                                        for uvrstitev in re.finditer(mestoRegex,datotekaTekma[counter-3]):
                                                 dict['mesto']= uvrstitev['mesto']
                                                 writer.writerow(dict)
                                                 gremoven=True
                                                 break
                                        if gremoven:
                                            gremoven2=True
                                            break
                                    if gremoven2:
                                        break
                                        
                                    counter+=1
                            os.remove(str(id))



def shrani_vse(id):
    shrani_skakalca(id)
    zdruzi_strani(id)
    tekme_csv(id)
