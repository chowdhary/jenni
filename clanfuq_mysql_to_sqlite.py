#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys
import sqlite3 as sql

def copy_message_history(mcon, scon):
    #userID, message
    print "copying message_history"
    scur = scon.cursor()
    mcur = mcon.cursor()
    scur.execute("DROP TABLE IF EXISTS message_history")
    scur.execute("CREATE TABLE `message_history` (`userID` bigint DEFAULT (0) NOT NULL, `message` text NOT NULL, `dateStamp` timestamp NOT NULL, CHECK (`userID` >= 0))")
    mcur.execute("select count(*) from message_history")
    mrows = mcur.fetchone()
    total_rows = mrows[0]
    cur_row = 0
    num_rows_per_query = 1000
    print "found %d rows, processing %d at a time" % (total_rows, num_rows_per_query)
    while cur_row < total_rows:
        print "processing rows %d to %d" % (cur_row, cur_row+num_rows_per_query)
        mcur.execute("select userID, message, dateStamp from message_history limit %s, %s", (cur_row, num_rows_per_query))
        mrows = mcur.fetchall()
        for mrow in mrows:
            scur.execute("insert into message_history (userID, message, dateStamp) values(?,?,?)", (mrow[0], unicode(mrow[1].strip('\r\n'),'latin-1'), mrow[2]))
        scon.commit()
        cur_row += num_rows_per_query
        print "cur_row = %d" % (cur_row)
    print "copied message_history"

def copy_words(mcon, scon):
    #wordID, word
    print "copying words"
    scur = scon.cursor()
    mcur = mcon.cursor()
    scur.execute("DROP TABLE IF EXISTS words")
    scur.execute("CREATE TABLE `words` (`wordID` integer NOT NULL PRIMARY KEY AUTOINCREMENT, `word` varchar(255) NOT NULL)")
    mcur.execute("select count(*) from words")
    mrows = mcur.fetchone()
    total_rows = mrows[0]
    cur_row = 0
    num_rows_per_query = 1000
    print "found %d rows, processing %d at a time" % (total_rows, num_rows_per_query)
    while cur_row < total_rows:
        print "processing rows %d to %d" % (cur_row, cur_row+num_rows_per_query)
        mcur.execute("select wordID, word from words limit %s, %s", (cur_row, num_rows_per_query))
        mrows = mcur.fetchall()
        for mrow in mrows:
            scur.execute("insert into words (wordID, word) values(?,?)", (mrow[0], unicode(mrow[1].strip('\r\n'),'latin-1')))
        scon.commit()
        cur_row += num_rows_per_query
        print "cur_row = %d" % (cur_row)
    print "copied words"

def copy_users(mcon, scon):
    #userID, hostname, handle, dateSeen, admin
    print "copying users"
    scur = scon.cursor()
    mcur = mcon.cursor()
    scur.execute("DROP TABLE IF EXISTS users")
    scur.execute("CREATE TABLE `users` (`userID` integer NOT NULL PRIMARY KEY AUTOINCREMENT, `hostname` varchar(255) NOT NULL, `handle` varchar(255) NOT NULL, `dateSeen` timestamp DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')) NOT NULL, `admin` boolean DEFAULT (0) NOT NULL)")
    mcur.execute("select count(*) from users")
    mrows = mcur.fetchone()
    total_rows = mrows[0]
    cur_row = 0
    num_rows_per_query = 1000
    print "found %d rows, processing %d at a time" % (total_rows, num_rows_per_query)
    while cur_row < total_rows:
        print "processing rows %d to %d" % (cur_row, cur_row+num_rows_per_query)
        mcur.execute("select userID, hostname, handle, dateSeen, admin from users limit %s, %s", (cur_row, num_rows_per_query))
        mrows = mcur.fetchall()
        for mrow in mrows:
            scur.execute("insert into users (userID, hostname, handle, dateSeen, admin) values(?,?,?,?,?)", (mrow[0], mrow[1], mrow[2], mrow[3], mrow[4]))
        scon.commit()
        cur_row += num_rows_per_query
        print "cur_row = %d" % (cur_row)
    print "copied users"

def copy_defitions(mcon, scon):
    #wordID, userID, definition
    print "copying definitions"
    scur = scon.cursor()
    mcur = mcon.cursor()
    scur.execute("DROP TABLE IF EXISTS definitions")
    scur.execute("CREATE TABLE `definitions` (`wordID` bigint DEFAULT (0) NOT NULL, `userID` bigint DEFAULT (0) NOT NULL, `definition` text NOT NULL, `dateTime` timestamp DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')) NOT NULL, CHECK (`wordID` >= 0), CHECK (`userID` >= 0))")
    mcur.execute("select count(*) from definitions")
    mrows = mcur.fetchone()
    total_rows = mrows[0]
    cur_row = 0
    num_rows_per_query = 1000
    print "found %d rows, processing %d at a time" % (total_rows, num_rows_per_query)
    while cur_row < total_rows:
        print "processing rows %d to %d" % (cur_row, cur_row+num_rows_per_query)
        mcur.execute("select wordID, userID, definition, dateTime from definitions limit %s, %s", (cur_row, num_rows_per_query))
        mrows = mcur.fetchall()
        for mrow in mrows:
            scur.execute("insert into definitions (wordID, userID, definition, dateTime) values(?,?,?,?)", (mrow[0], mrow[1], unicode(mrow[2].strip('\r\n'),'latin-1'), mrow[3]))
            #print "definition is %s" % (unicode(mrow[2].strip('\r\n'), 'cp1252'))
        scon.commit()
        cur_row += num_rows_per_query
        print "cur_row = %d" % (cur_row)
    print "copied definitions"

def generate_words_definitions(mcon, scon):
    print "generating words and definitions"
    mcur = mcon.cursor()
    scur = scon.cursor()
    scur.execute("DROP TABLE IF EXISTS definitions")
    scur.execute("CREATE TABLE `definitions` (`wordID` bigint DEFAULT (0) NOT NULL, `userID` bigint DEFAULT (0) NOT NULL, `definition` text NOT NULL, `dateTime` timestamp DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')) NOT NULL, CHECK (`wordID` >= 0), CHECK (`userID` >= 0))")
    scur.execute("DROP TABLE IF EXISTS words")
    scur.execute("CREATE TABLE `words` (`wordID` integer NOT NULL PRIMARY KEY AUTOINCREMENT, `word` varchar(255) NOT NULL)")
    num_rows_per_query = 1000
    cur_row = 0
    mcur.execute("SELECT COUNT(*) FROM `message_history`")
    mrows = mcur.fetchone()
    total_rows = mrows[0]
    print "found %d rows, processing %d at a time" % (total_rows, num_rows_per_query)
    inserts = 0
    while cur_row < total_rows:
        print "processing rows %d to %d " % (cur_row, cur_row+num_rows_per_query)
        mcur.execute("select `userID`, `message`, `dateStamp` from `message_history` limit %s,%s", (cur_row, num_rows_per_query))
        mrows = mcur.fetchall()
        for mrow in mrows:
            userID = mrow[0]
            message = mrow[1].strip()
            dateStamp = mrow[2]
            fSpace = message.find(' ')
            if fSpace != -1:
                fWord = message[0:fSpace]
                sSpace = message.find(' ', fSpace+1)
                if sSpace != -1:
                    sWord = message[fSpace+1:sSpace].lower()
                    if sWord == "is":
                        word = fWord.lower()
                        scur.execute("SELECT `wordID` from `words` where `word`=?", (unicode(word.strip('\r\n'),'latin-1'),))
                        srow = scur.fetchone()
                        if srow:
                            wordID = srow[0]
                        else:
                            scur.execute("INSERT INTO `words`(`word`) VALUES(?)", (unicode(word.strip('\r\n'),'latin-1'),))
                            wordID = scur.lastrowid
                            inserts+=1
                        scur.execute("INSERT INTO `definitions`(`wordID`,`userID`,`definition`,`dateTime`) VALUES(?,?,?,?)", (wordID,userID,unicode(message.strip('\r\n'),'latin-1'),dateStamp))
                        inserts+=1
            if inserts >= 1000:
                scon.commit()
                inserts = 0
        cur_row += num_rows_per_query
        print "cur_row = %d" % cur_row

    mcur.execute("select count(*) from definitions")
    mrows = mcur.fetchone()
    total_rows = mrows[0]
    cur_row = 0
    inserts = 0
    print "found %d rows, processing %d at a time" % (total_rows, num_rows_per_query)
    while cur_row < total_rows:
        print "processing rows %d to %d " % (cur_row, cur_row+num_rows_per_query)
        mcur.execute("select wordID, userID, definition, dateTime from definitions limit %s,%s", (cur_row, num_rows_per_query))
        mrows = mcur.fetchall()
        for mrow in mrows:
            wordID = mrow[0]
            userID = mrow[1]
            message = mrow[2].strip()
            dateTime = mrow[3]
            fSpace = message.find(' ')
            if fSpace != -1:
                fWord = message[0:fSpace]
                sSpace = message.find(' ', fSpace+1)
                if sSpace != -1:
                    sWord = message[fSpace+1:sSpace].lower()
                    if sWord == "is":
                        word = fWord.lower()
                        scur.execute("SELECT `wordID` from `words` where `word`=?", (unicode(word.strip('\r\n'),'latin-1'),))
                        srow = scur.fetchone()
                        if srow:
                            wordID = srow[0]
                        else:
                            scur.execute("INSERT INTO `words`(`word`) VALUES(?)", (unicode(word.strip('\r\n'),'latin-1'),))
                            wordID = scur.lastrowid
                            inserts+=1
                        scur.execute("INSERT INTO `definitions`(`wordID`,`userID`,`definition`,`dateTime`) VALUES(?,?,?,?)", (wordID,userID,unicode(message.strip('\r\n'),'latin-1'),dateStamp))
                        inserts+=1
                    if inserts >= 1000:
                        scon.commit()
                        inserts = 0
        cur_row += num_rows_per_query
        print "cur_row = %d" % cur_row

    scon.commit()

try:
    mcon = mdb.connect('localhost', 'root', 'thisisit', 'clanfuq')
    scon = sql.connect('clanfuq.db')
    #copy_message_history(mcon, scon)
    #copy_users(mcon, scon)
    generate_words_definitions(mcon, scon)
    #copy_words(mcon, scon)
    #copy_defitions(mcon, scon)

except mdb.Error as e:
    print "Error %d: %s" % (e.args[0], e.args[1])

except sql.Error as s:
    print "Error %s:" % s.args[0]

finally:
    if mcon:
        mcon.close()
    if scon:
        scon.close()
