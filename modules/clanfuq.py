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

def get_wordID(word):
    global db
    try:
        debug_p("getting wordID for '%s'" % word)
        con = sql.connect(db)
        cur = con.cursor()
        cur.execute("SELECT `wordID` FROM `words` WHERE `word`=?", (word,))
        row = cur.fetchone()
        if row:
            debug_p("found wordID: %s" % row[0])
            wordID = row[0]
        else:
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
    #print string
    pass

def clanfuq(jenni, input):
    debug_p("jenni: %s and input: %s" % (jenni.name, input.full_ident))
    if jenni.nick == input.nick:
        debug_p("self, returning")
        return
    created = datetime.datetime.now()
    text = input.group()
    text = text.strip()
    words = text.split()
    debug_p(repr(input.admin))
    userID = get_userID(input, created)
    debug_p("provided userID: %s" % userID)
    add_message_history(input, userID, created)
    debug_p("added message_history")
    if len(words) == 1 and words[0].endswith("?"):
        word = words[0].rstrip("?")
        debug_p("get definition of '%s'" % word)
        wordID = get_wordID(word)
        debug_p("provided wordID: %s" % wordID)
        definition = get_definition(wordID)
        debug_p("provided definition: %s" % definition)
        if definition:
            jenni.say(definition)
    elif len(words) > 2 and words[1] == "is":
        word = words[0]
        debug_p("adding definition for '%s'" % word)
        wordID = get_wordID(word)
        debug_p("provided wordID: %s" % wordID)
        add_definition(input, wordID, userID, created)
        debug_p("added definition")
clanfuq.rule = r'.*'

#def write_addquote(text):
#    fn = open('quotes.txt', 'a')
#    output = uc.encode(text)
#    fn.write(output)
#    fn.write('\n')
#    fn.close()
#
#
#def addquote(jenni, input):
#    '''.addquote <nick> something they said here -- adds the quote to the quote database.'''
#    text = input.group(2)
#    if not text:
#        return jenni.say('No quote provided')
#
#    write_addquote(text)
#
#    jenni.reply('Quote added.')
#addquote.commands = ['addquote']
#addquote.priority = 'low'
#addquote.example = '.addquote'
#
#
#def retrievequote(jenni, input):
#    '''.quote <number> -- displays a given quote'''
#    NO_QUOTES = 'There are currently no quotes saved.'
#    text = input.group(2)
#    try:
#        fn = open('quotes.txt', 'r')
#    except:
#        return jenni.reply('Please add a quote first.')
#
#    lines = fn.readlines()
#    if len(lines) < 1:
#        return jenni.reply(NO_QUOTES)
#    MAX = len(lines)
#    fn.close()
#    random.seed()
#    try:
#        number = int(text)
#        if number < 0:
#            number = MAX - abs(number) + 1
#    except:
#        number = random.randint(1, MAX)
#    if not (0 <= number <= MAX):
#        jenni.reply("I'm not sure which quote you would like to see.")
#    else:
#        if lines:
#            if number == 1:
#                line = lines[0]
#            elif number == 0:
#                return jenni.say('There is no "0th" quote!')
#            else:
#                line = lines[number - 1]
#            jenni.say('Quote %s of %s: ' % (number, MAX) + line)
#        else:
#            jenni.reply(NO_QUOTES)
#retrievequote.commands = ['quote']
#retrievequote.priority = 'low'
#retrievequote.example = '.quote'
#
#
#def delquote(jenni, input):
#    '''.rmquote <number> -- removes a given quote from the database. Can only be done by the owner of the bot.'''
#    if not input.owner:
#        return
#    text = input.group(2)
#    number = int()
#
#    try:
#        fn = open('quotes.txt', 'r')
#    except:
#        return jenni.reply('No quotes to delete.')
#
#    lines = fn.readlines()
#    MAX = len(lines)
#    fn.close()
#
#    try:
#        number = int(text)
#    except:
#        jenni.reply('Please enter the quote number you would like to delete.')
#        return
#
#    if number > 0:
#        newlines = lines[:number - 1] + lines[number:]
#    elif number == 0:
#        return jenni.reply('There is no "0th" quote!')
#    elif number == -1:
#        newlines = lines[:number]
#    else:
#        ## number < -1
#        newlines = lines[:number] + lines[number + 1:]
#    fn = open('quotes.txt', 'w')
#    for line in newlines:
#        txt = line
#        if txt:
#            fn.write(txt)
#            if txt[-1] != '\n':
#                fn.write('\n')
#    fn.close()
#    jenni.reply('Successfully deleted quote %s.' % (number))
#delquote.commands = ['rmquote', 'delquote']
#delquote.priority = 'low'
#delquote.example = '.rmquote'
#
#
#def grabquote(jenni, input):
#    try:
#        from modules import find
#    except:
#        return jenni.say('Could not load "find" module.')
#
#    txt = input.group(2)
#    parts = txt.split()
#    if not parts:
#        return jenni.say('Please provide me with a valid nick.')
#
#    nick = parts[0]
#    channel = input.sender
#    channel = (channel).lower()
#
#    quote_db = find.load_db()
#    if quote_db and channel in quote_db and nick in quote_db[channel]:
#        quotes_by_nick = quote_db[channel][nick]
#    else:
#        return jenni.say('There are currently no existing quotes by the provided nick in this channel.')
#
#    quote_by_nick = quotes_by_nick[-1]
#
#    quote = '<%s> %s' % (nick, quote_by_nick)
#
#    write_addquote(quote)
#
#    jenni.say('quote added: %s' % (quote))
#grabquote.commands = ['grab']
#

if __name__ == '__main__':
    print __doc__.strip()
