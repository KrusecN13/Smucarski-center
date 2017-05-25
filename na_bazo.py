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
    cur.execute("Select * from tekmovalci where id = '%s'",[id])
    zeNot=cur.fetchone()
    if zeNot is None:
        shrani_skakalca(id)
        with open('tekmovalci/info_{i}'.format(i=id),'r') as tekmovalec:
            reader = csv.DictReader(tekmovalec)
            for vrstica in reader:
                cur.execute("INSERT INTO tekmovalci VALUES (%s, %s, %s, %s, %s, %s)",
                [id, vrstica["Rojstni_dan"], vrstica["Spol"], vrstica["status"], vrstica["Drzava"],
                vrstica["klub"]])

            
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
            cur.execute("INSERT INTO  rezultati VALUES (%s, %s, %s, %s, %s, %s, %s)",
            [id, vrstica["mesto"], vrstica["id_tekmovalca"], vrstica["prvi_skok"],
            vrstica["drugi_skok"], vrstica["drugi_tocke"], vrstica["skupaj_tocke"]])
            

            
##################
            

#@get('/')
#def index():
#    cur.execute("SELECT * FROM oseba ORDER BY priimek, ime")
#    return template('glavna.html', skakalci=cur)

#@get('/transakcije/:x/')
#def transakcije(x):
#    cur.execute("SELECT * FROM transakcija WHERE znesek > %s ORDER BY znesek, id", [int(x)])
#    return template('tekmovalec.html', x=x, tekmovalec=cur)


            



######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

# poženemo strežnik na portu 8080, glej http://localhost:8080/
#run(host='localhost', port=8080)


