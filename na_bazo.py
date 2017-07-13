#!/usr/bin/python
# -*- encoding: utf-8 -*-

from bottle import *
# uvozimo ustrezne podatke za povezavo
import auth as auth
import csv
from skokiDownload import *
# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

# odkomentiraj, če želiš sporočila o napakah
# debug(True)

#funkcije za spreminjanje formatov teksta tako, da ga lahko SQL bere
def v_datum(datum):
    #spremeni datum v tako verzijod a ga SQL lahko uporablja
    datum = datum[-4:len(datum)] + datum[2:5] + '-' + datum[0:2]
    return datum

def imePriimek(skupaj):
    #spremeni 'PRIIMEK Ime' v ['Ime','Priimek']
    razdeli = skupaj.split(' ')
    priimek = razdeli[0].capitalize()
    ime = ' '.join(razdeli[1:len(razdeli)])
    return (ime,priimek)
def aktiven(status):
    if status=='Active':
        return 'Skače'
    else:
        return 'Ne skače'



### ko dodajaš najprej preveri, če je podatek že notri


#polne tabelo tekmovalci
def dodaj_tekmovalca(id):
    cur.execute("Select * from tekmovalci where id = %s",[id])
    zeNot=cur.fetchone()
    if zeNot is None:
        shrani_skakalca(id)
        with open('tekmovalci/info_{i}'.format(i=id),'r') as tekmovalec:
            reader = csv.DictReader(tekmovalec)
            for vrstica in reader:
                (ime,priimek) = imePriimek(vrstica["ime"])
                cur.execute("INSERT INTO tekmovalci VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                [id, v_datum(vrstica["Rojstni_dan"]), vrstica["Spol"], vrstica["status"], vrstica["Drzava"],
                vrstica["klub"],ime,priimek])

            
    #polne tabelo tekme
        with open('tekmovalci/csv_{i}.txt'.format(i=id),'r') as tekme:
            reader = csv.DictReader(tekme)
            for vrstica in reader:
                cur.execute("Select * from tekme where id_tekme = %s",[vrstica['id']])
                zeNot=cur.fetchone()
                if zeNot is None:
                    shrani_tekmo(vrstica['id'])
                    cur.execute("INSERT INTO tekme VALUES (%s, %s, %s, %s, %s, %s)",
                    [vrstica["id"],vrstica["kategorija"], v_datum(vrstica["datum"]),vrstica["drzava"], vrstica["mesto"],  vrstica["disciplina"],
                    ])
                    dodaj_tekmoR(vrstica["id"])
            
    conn.commit()          
    
    
    #polne tabelo rezultati
def dodaj_tekmoR(id):
    with open('tekme/tekma_{i}.txt'.format(i=id),'r') as tekme:
        
        reader = csv.DictReader(tekme)
        for vrstica in reader:
            cur.execute("SELECT * FROM rezultati where id_tekme = %s AND id_tekmovalca = %s",
            [id,vrstica['id_tekmovalca']])
            zeNot= cur.fetchall()
            if zeNot == []:
                if vrstica["mesto"]=='':
                    vrstica["mesto"]=500
                    
                cur.execute("INSERT INTO  rezultati VALUES (%s, %s, %s)",
                [id, vrstica["mesto"], vrstica["id_tekmovalca"]])
                        
            
##            Na žalost imajo preveč nekonsistentno bazo, tako da tipi ne delujejo primerno, zato bomo dolocene dele kr izpustili, ce bo cas se mogoce lotimo popravljat njihove napake
##            cur.execute("SELECT * FROM rezultati where id_tekme = %s AND id_tekmovalca = %s",
##            [id,vrstica['id_tekmovalca']])
##            zeNot= cur.fetchall()
##            if zeNot == []:
##                #treba spremenit ničelne vnose v ničle.
##                if vrstica["prvi_tocke"] == '':
##                    vrstica["prvi_tocke"]=0
##                if vrstica["drugi_tocke"] == '':
##                    vrstica["drugi_tocke"] = 0
##                if vrstica["skupaj_tocke"] == '':
##                    vrstica["skupaj_tocke"] = 0
##                if vrstica["drugi_skok"] == '':
##                    vrstica["drugi_skok"] = 0
##                if vrstica["prvi_skok"] == '':
##                    vrstica["prvi_skok"]= 0
##                if vrstica["mesto"]=='':
##                    vrstica["mesto"] = 500
##                skupToc=str(vrstica["skupaj_tocke"])
##                if skupToc[-2:len(skupToc)]== '.0':
##                    #to je tu samo zato ker imajo v bazi neke napake na fisu pa so se skupaj tocke vcasih pojavile kot "91,5.0", ce bi bile prav zapisane in bi odstranili .0 ni nič narobe
##                    #zato bomo vedno to nardili, pa se nebi smelo nič pokvariti
##                    vrstica["skupaj_tocke"] = skupToc[0:-2]
##                
##                cur.execute("INSERT INTO  rezultati VALUES (%s, %s, %s, %s, %s,%s,%s, %s)",
##                [id, vrstica["mesto"], vrstica["id_tekmovalca"], vrstica["prvi_skok"],vrstica["prvi_tocke"],
##                vrstica["drugi_skok"], vrstica["drugi_tocke"], vrstica["skupaj_tocke"]])
##            


            
##################SPLETNA STRAN LAHKO JO DAMO DRUGAM CE NAM USPE
            


@route('/odstrani_tekmovalca/:x', method='POST')
def odstrani_skakalca(x):
    ime = request.forms.get("ime")
    geslo = request.forms.get("geslo")
    cur.execute("SELECT id_uporabnika FROM uporabnik WHERE ime=%s",[ime])
    id_uporabnika = cur.fetchone()
    cur.execute("DELETE FROM mojiskakalci WHERE uporabnik = %s AND skakalec = %s",[id_uporabnika[0],x])
    conn.commit()
    return template('odstrani_tekmovalca.html',sezIme=[[ime,geslo]])

@route('/moji_skakalci/',method='POST')
def moji_skakalci():
    ime = request.forms.get("ime")
    geslo = request.forms.get("geslo")
    ime_skakalca=request.forms.get("skakalec_ime")
    priimek_skakalca=request.forms.get("skakalec_priimek")
    if ime == '' or ime==None:
        #Če si nismo izbrali imena ko smo se vpisovali
        redirect('/')
    cur.execute("SELECT * FROM uporabnik where ime=%s",[ime])
    #poisce, ce je uporabnik v bazi
    pravoGeslo= cur.fetchone()
    if pravoGeslo == None:
        #ce ga ni, ga doda
        cur.execute("INSERT INTO uporabnik (ime, geslo) VALUES (%s, %s)",[ime,geslo])
        conn.commit()
        cur.execute("SELECT id_uporabnika FROM uporabnik WHERE ime=%s",[ime])
        id_uporabnika = cur.fetchone()
        cur.execute("SELECT id,drzava,ime,priimek FROM tekmovalci INNER JOIN mojiskakalci ON tekmovalci.id = mojiskakalci.skakalec WHERE uporabnik = %s",[id_uporabnika[0]])
        return template('glavna.html', skakalci=cur,sezIme=[[ime,geslo]],obstaja=[''])
    else:
        if pravoGeslo['geslo'] == geslo:
        #ce je, je treba pogledat ce je geslo pravo

            
            if ime_skakalca != '' and ime_skakalca != None:
                #preveri ce je uporabnik zelel dodati skakalca, ce je, ga doda.
                if priimek_skakalca !='' and priimek_skakalca != None:
                    idskakalca = najdi_id(ime_skakalca,priimek_skakalca)
                    #če slučajno idja ne najde, naj vrne napako
                    if idskakalca != None:
                        dodaj_tekmovalca(idskakalca)
                        cur.execute("SELECT id_uporabnika FROM uporabnik WHERE ime=%s",[ime])
                        id_uporabnika = cur.fetchone()
                        cur.execute("SELECT * FROM mojiskakalci WHERE uporabnik=%s AND skakalec=%s",[id_uporabnika[0],idskakalca])
                        zeNot= cur.fetchone()
                        #preveri, če je skakalec ze med skakalci uporabnika
                        if zeNot==None:
                                cur.execute("INSERT INTO mojiskakalci VALUES (%s,%s)",[id_uporabnika[0],idskakalca])
                                conn.commit()
                    else:
                        cur.execute("SELECT id_uporabnika FROM uporabnik WHERE ime=%s",[ime])
                        id_uporabnika = cur.fetchone()
                        cur.execute("SELECT id,drzava,ime,priimek FROM tekmovalci INNER JOIN mojiskakalci ON tekmovalci.id = mojiskakalci.skakalec WHERE uporabnik = %s",[id_uporabnika[0]])
                        return template('glavna.html', skakalci=cur,sezIme=[[ime,geslo]],obstaja=['Skakalec ne obstaja'])
            cur.execute("SELECT id_uporabnika FROM uporabnik WHERE ime=%s",[ime])
            id_uporabnika = cur.fetchone()
            cur.execute("SELECT id,drzava,ime,priimek FROM tekmovalci INNER JOIN mojiskakalci ON tekmovalci.id = mojiskakalci.skakalec WHERE uporabnik = %s",[id_uporabnika[0]])
            return template('glavna.html', skakalci=cur,sezIme=[[ime,geslo]],obstaja=[''])
            
        else:
        #ce geslo ni pravo
            redirect('/wrong_login')
    

   
    
@route ('/wrong_login')
def wrong_login():
    return template('wrong_login.html')
    
@route ('/tekmovalci/:x', method="POST")
def get_tekmovalec(x):
    ime = request.forms.get("ime")
    geslo = request.forms.get("geslo")
    cur.execute("SELECT rojstni_dan,spol,status,drzava,klub,ime,priimek FROM tekmovalci where id=%s",[x])
    info=cur.fetchall()
    info[0][2] = aktiven(info[0][2])
    #prevod v slovenscino
    cur.execute("SELECT rezultati.id_tekme, rezultati.mesto,tekme.kategorija, tekme.datum, tekme.drzava, tekme.disciplina FROM tekme INNER JOIN rezultati ON tekme.id_tekme = rezultati.id_tekme WHERE id_tekmovalca = %s ORDER BY tekme.datum DESC",[x])
    tekme=cur.fetchall()
    cur.execute("SELECT COUNT(id_tekme) FROM rezultati WHERE id_tekmovalca = %s AND mesto='1'",[x])
    stZmag=cur.fetchone()
    cur.execute("SELECT COUNT(id_tekme) FROM rezultati WHERE id_tekmovalca = %s AND mesto <4",[x])
    stStopnick = cur.fetchone()
    cur.execute("SELECT COUNT(id_tekme) FROM rezultati WHERE id_tekmovalca = %s",[x])
    stTekem=cur.fetchone()
    cur.execute("SELECT COUNT(rezultati.id_tekme) FROM rezultati INNER JOIN tekme ON rezultati.id_tekme = tekme.id_tekme WHERE id_tekmovalca =%s AND kategorija LIKE 'Olympic%%'",[x])
    olympicNastopi = cur.fetchone()
    cur.execute("SELECT COUNT(rezultati.id_tekme) FROM rezultati INNER JOIN tekme ON rezultati.id_tekme = tekme.id_tekme WHERE id_tekmovalca =%s AND kategorija LIKE 'Olympic%%' AND rezultati.mesto<4",[x])
    olympicStop = cur.fetchone()
    cur.execute("SELECT COUNT(rezultati.id_tekme) FROM rezultati INNER JOIN tekme ON rezultati.id_tekme = tekme.id_tekme WHERE id_tekmovalca =%s AND kategorija LIKE 'Olympic%%' AND rezultati.mesto=1",[x])
    olympicWin = cur.fetchone()
    return  template('tekmovalec.html', tekmovalec=info,sezIme=[[ime,geslo]],tekmice=tekme,stevZmag=stZmag,stevStopnick=stStopnick,olympicNastopi=olympicNastopi,olympicStop =olympicStop,olympicWin=olympicWin )

@route ('/primerjaj_tekmovalce/', method="POST")
def primerjaj_tekmovalce():
    idtekmovalci = request.forms.get("primerjava")
    idtekmovalci = idtekmovalci.split(',')
    ime = request.forms.get("ime")
    geslo = request.forms.get("geslo")
    tekmovalci=[]
    
    for x in idtekmovalci:
        stvari=[]
        cur.execute("SELECT ime,priimek FROM tekmovalci where id=%s",[x])
        imepriim=cur.fetchone()
        stvari.append(imepriim['ime'])
        stvari.append(imepriim['priimek'])
        cur.execute("SELECT COUNT(id_tekme) FROM rezultati WHERE id_tekmovalca = %s",[x])
        stvari += cur.fetchone()
        cur.execute("SELECT COUNT(id_tekme) FROM rezultati WHERE id_tekmovalca = %s AND mesto='1'",[x])
        stvari += cur.fetchone()
        cur.execute("SELECT COUNT(id_tekme) FROM rezultati WHERE id_tekmovalca = %s AND mesto <4",[x])
        stvari += cur.fetchone()
        cur.execute("SELECT COUNT(rezultati.id_tekme) FROM rezultati INNER JOIN tekme ON rezultati.id_tekme = tekme.id_tekme WHERE id_tekmovalca =%s AND kategorija LIKE 'Olympic%%'",[x])
        stvari += cur.fetchone()
        cur.execute("SELECT COUNT(rezultati.id_tekme) FROM rezultati INNER JOIN tekme ON rezultati.id_tekme = tekme.id_tekme WHERE id_tekmovalca =%s AND kategorija LIKE 'Olympic%%' AND rezultati.mesto<4",[x])
        stvari += cur.fetchone()
        cur.execute("SELECT COUNT(rezultati.id_tekme) FROM rezultati INNER JOIN tekme ON rezultati.id_tekme = tekme.id_tekme WHERE id_tekmovalca =%s AND kategorija LIKE 'Olympic%%' AND rezultati.mesto=1",[x])
        stvari += cur.fetchone()
        tekmovalci.append(stvari)
    return template('primerjaj_tekmovalce',tekmovalci=tekmovalci,sezIme=[[ime,geslo]])

@route ('/moj_racun/', method="POST")
def moj_racun():
    geslo1=request.forms.get("geslo1")
    geslo2=request.forms.get("geslo2")
    ime = request.forms.get("ime")
    geslo = request.forms.get("geslo")
    cur.execute("SELECT * FROM uporabnik where ime=%s",[ime])
    #poisce, ce je uporabnik v bazi
    pravoGeslo= cur.fetchone()
    if pravoGeslo != None:
        if pravoGeslo['geslo'] == geslo:
            if geslo1 != None:
                if geslo1==geslo2:
                    cur.execute('UPDATE uporabnik SET geslo = %s WHERE ime = %s',[geslo1,ime])
                    conn.commit()
                    return template('myAcc.html',sezIme=[[ime,geslo1]],menjava=['Menjava je bila uspešna'])
                else:
                    return template('myAcc.html',sezIme=[[ime,geslo]],menjava=['Gesli se ne ujemata'])

            return template('myAcc.html',sezIme=[[ime,geslo]],menjava=[''])
    

@route('/')
def index():
    return template('login.html')



######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

#poženemo strežnik na portu 8080, glej http://localhost:8080/
run(host='localhost', port=8080)


