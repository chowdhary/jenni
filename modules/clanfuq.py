#!/usr/bin/env python
"""
clanfuq.py - jenni Clanfuq Module

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import datetime
import sqlite3 as sql
from modules import unicode as uc

db = 'clanfuq.db'

def get_userID(input, created):
    global db
    try:
        username = input.nick
        full_ident = input.full_ident
        admin = 0
        if input.admin:
            admin = 1
        con = sql.connect(db)
        cur = con.cursor()
        cur.execute("SELECT `userID` FROM `users` WHERE `hostname`=? AND `handle`=? and `admin`=?", (full_ident,username,admin))
        row = cur.fetchone()
        if row:
            userID = row[0]
            cur.execute("UPDATE `users` SET `dateSeen`=? WHERE `userID`=?", (created,userID))
        else:
            cur.execute("INSERT INTO `users`(`hostname`,`handle`,`dateSeen`,`admin`) VALUES(?,?,?,?)", (full_ident,username,created,admin))
            userID = cur.lastrowid
        con.commit()
        return userID
    except sql.Error, e:
        print "Error %s:" % e.args[0]
    finally:
        if con:
            con.close()

def add_message_history(input, userID, created):
    global db
    try:
        con = sql.connect(db)
        cur = con.cursor()
        cur.execute("INSERT INTO `message_history`(`userID`,`message`,`dateStamp`) VALUES(?,?,?)", (userID, input.group(), created))
        con.commit()
    except sql.Error, e:
        print "Error %s:" % e.args[0]
    finally:
        if con:
            con.close()

def get_wordID(word, doInsert):
    global db
    try:
        debug_p("getting wordID for '%s'" % word)
        con = sql.connect(db)
        cur = con.cursor()
        cur.execute("SELECT `wordID` FROM `words` WHERE `word`=?", (word,))
        row = cur.fetchone()
        wordID = None
        if row:
            debug_p("found wordID: %s" % row[0])
            wordID = row[0]
        elif doInsert:
            cur.execute("INSERT INTO `words`(`word`) VALUES(?)", (word,))
            wordID = cur.lastrowid
            debug_p("inserted %s" % wordID)
            con.commit()
        return wordID
    except sql.Error, e:
        print "Error %s:" % e.args[0]
    finally:
        if con:
            con.close()

def add_definition(input, wordID, userID, created):
    global db
    try:
        con = sql.connect(db)
        cur = con.cursor()
        #cur.execute("CREATE TABLE IF NOT EXISTS `definitions` (`id` INTEGER PRIMARY KEY AUTOINCREMENT,`word` TEXT NOT NULL, `definition` TEXT NOT NULL, `username` TEXT NOT NULL, `created` INTEGER NOT NULL);")
        #cur.execute("INSERT INTO `definitions`(`word`,`definition`,`username`,`created`) VALUES(?,?,?,?)", (word,definition,username,created))
        cur.execute("INSERT INTO `definitions`(`wordID`,`userID`,`definition`,`dateTime`) VALUES(?,?,?,?)", (wordID,userID,input.group(),created))
        con.commit()
    except sql.Error, e:
        print "Error %s:" % e.args[0]
    finally:
        if con:
            con.close()


def get_definition(wordID):
    global db
    try:
        con = sql.connect(db)
        cur = con.cursor()
        #cur.execute("SELECT `definition` FROM `definitions` WHERE `word`=? ORDER BY `id` DESC LIMIT 1", (word,))
        cur.execute("SELECT `definition` FROM `definitions` WHERE `wordID`=? ORDER BY `dateTime` DESC LIMIT 0,1", (wordID,))
        row = cur.fetchone()
        if row:
            return row[0]
        return None
    except sql.Error, e:
        print "Error %s:" % e.args[0]
    finally:
        if con:
            con.close()

def debug_p(string):
    print string
    pass

def clanfuq(jenni, input):
    debug_p("jenni: %s and input: %s" % (jenni.name, input.full_ident))
    if jenni.nick == input.nick:
        debug_p("self, returning")
        return
    created = datetime.datetime.now()
    text = input.group()
    text = text.strip()
    debug_p(repr(input.admin))
    userID = get_userID(input, created)
    debug_p("provided userID: %s" % userID)
    add_message_history(input, userID, created)
    debug_p("added message_history")
    qIdx = text.find('?')
    if qIdx != -1:
        qWord = text[0:qIdx].lower()
        debug_p("get definition of '%s'" % qWord)
        wordID = get_wordID(qWord, False)
        debug_p("provided wordID: %s" % wordID)
        if wordID:
            definition = get_definition(wordID)
            debug_p("provided definition: %s" % definition)
            if definition:
                jenni.say(definition)
    fSpace = text.find(' ')
    if fSpace != -1:
        fWord = text[0:fSpace]
        sSpace = text.find(' ', fSpace+1)
        if sSpace != -1:
            sWord = text[fSpace+1:sSpace].lower()
            if sWord == "is":
                word = fWord.lower()
                debug_p("adding definition for '%s'" % word)
                wordID = get_wordID(word, True)
                debug_p("provided wordID: %s" % wordID)
                add_definition(input, wordID, userID, created)
                debug_p("added definition")
clanfuq.rule = r'.*'

if __name__ == '__main__':
    print __doc__.strip()
