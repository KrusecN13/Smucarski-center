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
                cur.execute("INSERT INTO tekmovalci VALUES (%s, %s, %s, %s, %s, %s, %s)",
                [id, vrstica["Rojstni_dan"], vrstica["Spol"], vrstica["status"], vrstica["Drzava"],
                vrstica["klub"],vrstica["ime"]])

            
    #polne tabelo tekme
        with open('tekmovalci/csv_{i}.txt'.format(i=id),'r') as tekme:
            reader = csv.DictReader(tekme)
            for vrstica in reader:
                cur.execute("Select * from tekme where id_tekme = %s",[vrstica['id']])
                zeNot=cur.fetchone()
                if zeNot is None:
                    shrani_tekmo(vrstica['id'])
                    cur.execute("INSERT INTO tekme VALUES (%s, %s, %s, %s, %s, %s)",
                    [vrstica["id"], vrstica["datum"], vrstica["uvrstitev"], vrstica["drzava"], vrstica["mesto"],
                    vrstica["disciplina"]])
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
            if zeNot == None:
                cur.execute("INSERT INTO  rezultati VALUES (%s, %s, %s, %s, %s, %s, %s)",
                [id, vrstica["mesto"], vrstica["id_tekmovalca"], vrstica["prvi_skok"],
                vrstica["drugi_skok"], vrstica["drugi_tocke"], vrstica["skupaj_tocke"]])
            


            
##################SPLETNA STRAN LAHKO JO DAMO DRUGAM CE NAM USPE
            


@route('/odstrani_tekmovalca/:x',method='POST')
def odstrani_skakalca(x):
    ime = request.forms.get("ime")
    geslo = request.forms.get("geslo")
    cur.execute("DELETE FROM mojiskakalci WHERE uporabnik = %s AND skakalec = %s",[ime,x])
    conn.commit()
    return template('odstraniTekmovalca.html',sezIme=[[ime,geslo]])

@route('/moji_skakalci/',method='POST')
def moji_skakalci():
    ime = request.forms.get("ime")
    geslo = request.forms.get("geslo")
    ime_skakalca=request.forms.get("skakalec_ime")
    priimek_skakalca=request.forms.get("skakalec_priimek")
    if ime == '' or ime==None:
        redirect('/')
    cur.execute("SELECT * FROM uporabnik where ime=%s",[ime])
    pravoGeslo= cur.fetchone()
    if pravoGeslo == None:
        cur.execute("INSERT INTO uporabnik VALUES (%s, %s)",[ime,geslo])
        conn.commit()
        cur.execute("SELECT id,drzava,ime FROM tekmovalci INNER JOIN mojiskakalci ON tekmovalci.id = mojiskakalci.skakalec WHERE uporabnik = %s",[ime])
        return template('glavna.html', skakalci=cur,sezIme=[[ime,geslo]])
    else:
        if pravoGeslo['geslo'] == geslo: 
            if ime_skakalca != None:
                if priimek_skakalca !=None:
                    idskakalca = najdi_id(ime_skakalca,priimek_skakalca)
                    dodaj_tekmovalca(idskakalca)
                    cur.execute("SELECT * FROM mojiskakalci WHERE uporabnik=%s AND skakalec=%s",[ime,idskakalca])
                    zeNot= cur.fetchone()
                    if zeNot==None:
                            cur.execute("INSERT INTO mojiskakalci VALUES (%s,%s)",[ime,idskakalca])
                            conn.commit()
            cur.execute("SELECT id,drzava,ime FROM tekmovalci INNER JOIN mojiskakalci ON tekmovalci.id = mojiskakalci.skakalec WHERE uporabnik = %s",[ime])
            return template('glavna.html', skakalci=cur,sezIme=[[ime,geslo]])
            
        else:
            return "Napacno geslo"
    

   
    


@route ('/tekmovalci/:x', method="POST")
def get_tekmovalec(x):
    ime = request.forms.get("ime")
    geslo = request.forms.get("geslo")
    cur.execute("SELECT rojstni_dan,spol,status,drzava,klub,ime FROM tekmovalci where id=%s",[x])
    info=cur.fetchall()
    cur.execute("SELECT rezultati.id_tekme, rezultati.mesto,tekme.kategorija, tekme.datum, tekme.drzava, tekme.disciplina FROM tekme INNER JOIN rezultati ON tekme.id_tekme = rezultati.id_tekme WHERE id_tekmovalca = %s",[x])
    tekme=cur.fetchall()
    cur.execute("SELECT COUNT(id_tekme) FROM rezultati WHERE id_tekmovalca = %s AND mesto='1'",[x])
    stZmag=cur.fetchone()
    cur.execute("SELECT COUNT(id_tekme) FROM rezultati WHERE id_tekmovalca = %s AND mesto IN ('1','2','3')",[x])
    stStopnick = cur.fetchone()
    return  template('tekmovalec.html', tekmovalec=info,sezIme=[[ime,geslo]],tekmice=tekme,stevZmag=stZmag,stevStopnick=stStopnick)




@route('/')
def index():
    #cur.execute("SELECT id,drzava,ime FROM tekmovalci")
    return template('login.html')



######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

#poženemo strežnik na portu 8080, glej http://localhost:8080/
run(host='localhost', port=8080)


