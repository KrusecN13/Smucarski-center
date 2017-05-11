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


def dodaj_tekmo(id):
    with open('tekme/tekma_{i}.txt'.format(i=id),'r') as tekme:
        reader = csv.DictReader(tekme)
        for vrstica in reader:
            cur.execute("INSERT INTO  rezultati VALUES({i},{mesto}, {id_tekmovalca}, {prvi_skok}, {prve_tocke}, {drugi_skok}, {druge_tocke}, {skupaj_tocke})".format(i=id,mesto=vrstica[mesto],id_tekmovalca=vrstica[id_tekmovalca], prvi_skok = vrstica[prvi_skok], drugi_skok = vrstica[drugi_skok],druge_tocke = vrstica[druge_tocke],skupaj_tocke = vrstica[skupaj_tocke]))

            
    print('Tekma {id} je bila dodana.'.format(id))



######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 



dodaj_tekmo(2312)
