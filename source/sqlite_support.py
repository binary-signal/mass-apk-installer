#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
 Name:        sqlite_support
 Author:      Evaggelos Mouroutsos

 Created:     19/10/2011
 Last Modified: 22/11/2016
 Copyright:   (c) Evaggelos Mouroutsos 2016
 Licence:
 Copyright (c) 2016, Evaggelos Mouroutsos
 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions are met:
     * Redistributions of source code must retain the above copyright
       notice, this list of conditions and the following disclaimer.
     * Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.
     * Neither the name of the <organization> nor the
       names of its contributors may be used to endorse or promote products
       derived from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 vWARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
 DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.   """""

import sqlite3 as lite
import sys
import hashlib

def make_hash_sha256 (filename):
    # make sha256 object
    sha256 = hashlib.sha256()
    sha256.update(filename)
    return sha256.hexdigest()

DBNAME = "backup.db"

def db_connect(dbname=DBNAME):
    con = None
    try:
        con = lite.connect('backup.db')
    except lite.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)

    finally:
        return con


def db_insert(con, apkInfo): #apkInfo is a dictionary
    with con:
        cur = con.cursor()
        id = make_hash_sha256(apkInfo['name'])
        name = apkInfo['name']
        vc = apkInfo['versionCode']
        vn = apkInfo['versionName']

        #clean version number  from quotes before insert in db
        vc = vc.replace("'", "");


        q="INSERT INTO apk(name,versioncode, versionname,hash) VALUES("+name+","+vc+","+ vn+","+"'"+ id+"');"
        cur.execute(q)


def db_empty_apk_table(con):
    q = "delete from " + "apk"
    with con:
        cur = con.cursor()
        cur.execute(q)


def db_init(con):
    try:
        if con == None:
            con = db_connect(DBNAME)

        with con:
            cur = con.cursor()
            cur.execute("CREATE TABLE apk(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, versioncode INT, versionName TEXT, hash TEXT)")
            con.close()
    except lite.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)
    finally:
        print "Database" + DBNAME + " initiliased"


con = None

#db_init(con)
#con = db_connect(DBNAME)
#db_insert(con,apk_version)
#db_empty_apk_table(con)


