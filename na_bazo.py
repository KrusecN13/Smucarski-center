#!/usr/bin/python
# -*- encoding: utf-8 -*-


# uvozimo ustrezne podatke za povezavo
import auth as auth
import csv

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

# odkomentiraj, če želiš sporočila o napakah
# debug(True)


### ko dodajaš najprej preveri, če je podatek že notri

def dodaj_tekmovalca(id):
    #polne tabelo tekmovalci
    with open('tekmovalci/info_{i}.txt'.format(i=id),'r') as tekmovalec:
        reader = csv.DictReader(tekmovalec)
        for vrstica in reader:
            cur.execute("INSERT INTO tekmovalci VALUES (%s, %s, %s, %s, %s, %s)",
            [id, vrstica["rojstni_dan"], vrstica["spol"], vrstica["status"], vrstica["drzava"],
            vrstica["klub"]])

            
    #polne tabelo tekme
    with open('tekmovalci/csv_{i}.txt'.format(i=id),'r') as tekme:
        reader = csv.DictReader(tekme)
        for vrstica in reader:
            cur.execute("INSERT INTO tekme VALUES (%s, %s, %s, %s, %s, %s)",
            [vrstica["id"], vrstica["datum"], vrstica["uvrstitev"], vrstica["drzava"], vrstica["mesto"],
            vrstica["disciplina"]])
            dodaj_tekmo(vrstica["id"])
    
    
    #polne tabelo rezultati
def dodaj_tekmo(id):
    with open('tekme/tekma_{i}.txt'.format(i=id),'r') as tekme:
        reader = csv.DictReader(tekme)
        for vrstica in reader:
            cur.execute("INSERT INTO  rezultati VALUES (%s, %s, %s, %s, %s, %s, %s)",
            [id, vrstica["mesto"], vrstica["id_tekmovalca"], vrstica["prvi_skok"],
            vrstica["drugi_skok"], vrstica["druge_tocke"], vrstica["skupaj_tocke"]])
            
    conn.commit()
            
    print('Tekma {id} je bila dodana.'.format(id))



######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 



dodaj_tekmo(2312)
