#!/usr/bin/env python
'''
units.py - jenni Units Module
Copyright 2013, Michael Yanovich (yanovich.net)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
'''

from modules import proxy
from modules import unicode as uc
import datetime as dt
import json
import re

exchange_rates = dict()
last_check = dt.datetime.now()
exchanges = ['btce', 'rock', 'ripple', 'bitstamp', 'coinbase']


def btc_page():
    try:
        page = proxy.get('https://api.bitcoincharts.com/v1/markets.json')
    except Exception, e:
        print dt.datetime.now(), e
        return False, 'Failed to reach bitcoincharts.com'
    return True, page


def btc_coinbase_page():
    try:
        page = proxy.get('https://coinbase.com/api/v1/currencies/exchange_rates')
    except Exception, e:
        print dt.datetimenow.now(), e
        return False, 'Failed to reach coinbase.com'
    return True, page


def ppnum(num):
    return re.sub("(?!\..*)(\d)(?=(\d{3})+(?!\d))", r"\1,", "%.2f" % num)


def btc(jenni, input):
    '''.btc -- display the current prices for Bitcoins'''
    global exchange_rates
    global last_check

    now = dt.datetime.now()

    if (not exchange_rates) or (now - last_check > dt.timedelta(minutes=15)):
        status, page = btc_page()
        json_page = dict()

        if status:
            try:
                json_page = json.loads(page)
            except:
                pass

        else:
            return jenni.reply(page)

        ## build internal state of exchange
        for each in json_page:
            if each['currency'] == 'USD':
                if 'USD' not in exchange_rates:
                    exchange_rates['USD'] = dict()
                exchange_rates['USD'][each['symbol'].replace('USD', '')] = each['close']
        last_check = dt.datetime.now()

        coinbase_status, coinbase_page = btc_coinbase_page()

        try:
            coinbase_json = json.loads(coinbase_page)
        except:
            pass

        if type(coinbase_json['btc_to_usd']) is str:
            exchange_rates['USD']['coinbase'] = ppnum(float(coinbase_json['btc_to_usd'].replace(',','')))
        else:
            exchange_rates['USD']['coinbase'] = ppnum(float(coinbase_json['btc_to_usd']))

    split_input = input.split()
    if len(split_input) > 1:
        response = split_input[1]
        try:
            btc_amt = float(split_input[1].replace(',','')) if type(split_input[1]) is str else float(split_input[1])
            response = '{0} BTC = '.format(split_input[1])
            symbols = exchange_rates['USD'].keys()
            symbols.sort()
            first = True
            for each in symbols:
                if each.replace('USD', '') in exchanges:
                    if not first:
                        response += ' | '
                    first = False
                    response += '{}: {:.2f} USD'.format(each,
                            (float(exchange_rates['USD'][each].replace(',','')) * btc_amt 
                             if type(exchange_rates['USD'][each]) is str 
                             else float(exchange_rates['USD'][each]) * btc_amt))
        except ValueError:
            response = '%s is not a valid BTC amount' % (split_input[1])
    else:
        response = '1 BTC (in USD) = '
        symbols = exchange_rates['USD'].keys()
        symbols.sort()

        for each in symbols:
         if each.replace('USD', '') in exchanges:
             response += '%s: %s | ' % (each, exchange_rates['USD'][each])

        if type(exchange_rates['USD']['coinbase']) is str:
            response += 'lolcat (coinbase) index: $%s | ' % (ppnum(float(exchange_rates['USD']['coinbase'].replace(',','')) * 160))
            response += 'Howells (coinbase) index: $%s | ' % (ppnum(float(exchange_rates['USD']['coinbase'].replace(',','')) * 7500))
        else:
            response += 'lolcat (coinbase) index: $%s | ' % (ppnum(float(exchange_rates['USD']['coinbase']) * 160))
            response += 'Howells (coinbase) index: $%s | ' % (ppnum(float(exchange_rates['USD']['coinbase']) * 7500))

        response += 'last updated at: %s UTC' % (str(last_check))

    jenni.say(response)
btc.commands = ['btc']
btc.example = '.btc'
btc.rate = 20


def fbtc(jenni, input):
    '''.fbtc - returns prices from "The Fucking Bitcoin"'''
    try:
        page = proxy.get('http://thefuckingbitcoin.com/')
    except:
        return jenni.say('Could not access thefuckingbitcoin.com')

    price = re.search('<p id="lastPrice">(\S+)</p>', page)
    remarks = re.search('<p id="remark">(.*?)</p><p id="remarkL2">(.*?)</p>', page)

    try:
        remarks = remarks.groups()
    except:
        return jenni.say('Could not find relevant information.')

    resp = str()
    resp += '1 BTC == %s USD. ' % price.groups()

    if remarks:
        resp += '%s %s' % (remarks[0], remarks[1])

    jenni.say(resp)

fbtc.commands = ['fbtc']
fbtc.example = '.fbtc'
fbtc.rate = 20


if __name__ == '__main__':
    print __doc__.strip()
