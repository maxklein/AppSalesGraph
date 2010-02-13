# AppSalesGraph: AppStore Sales Graphing
# Copyright (c) 2010 by Max Klein (maximusklein@gmail.com)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.


import csv, sys
import datetime
import pickle
import settings

from dateutil.parser import *
 

class ExchangeRate(object):
	
	currencies = None
	currencies_to_update = []
	shutDown = False
	preLoad = False
	
	def __init__(self, currency, f, updated):
		self.last_updated = updated
		self.currency = currency
		self.fraction_of_1_usd = f

	@classmethod
	def requestShutdown(cls):
		ExchangeRate.shutDown = True
		
	@classmethod
	def save_currencies(cls):
		try:
			if not ExchangeRate.currencies is None:
				file = open(settings.DataDir("currencies.key"), "wb") # write mode
				file.write(pickle.dumps(ExchangeRate.currencies, 2))
				file.close()
		except:
			settings.log("Could not save currency data. Will try again on restart")
			
	@classmethod
	def update_currencies(cls):
		
		if ExchangeRate.currencies == None:
			ExchangeRate.currencies = {}
			
		for currency in ExchangeRate.currencies_to_update:
			if ExchangeRate.shutDown == True:
				break
			
			settings.log("Updating: " + currency)
			
			e = None
			if ExchangeRate.currencies.has_key(currency):
				e = ExchangeRate.currencies[currency]
			else:
				e = ExchangeRate(currency, 1.0, datetime.date.today() - datetime.timedelta(days=7))
				
			if e.last_updated.day != datetime.date.today().day:
				try:
					e = ExchangeRate(currency, download_exchange_rate(currency), datetime.date.today())
					ExchangeRate.currencies[currency] = e
				except:
					settings.log("Could not download todays currency")
					e = ExchangeRate.currencies[currency]


	@classmethod
	def get(self, currency):
		
		if not currency in ExchangeRate.currencies_to_update:
			ExchangeRate.currencies_to_update.append(currency)
		
		if ExchangeRate.preLoad == True:
			return
		
		file= None
		
		if ExchangeRate.currencies == None:
			ExchangeRate.currencies = {}
			try:
				file_name = settings.DataDir("currencies.key")
				file = open(file_name, "rb") # read mode
				info = file.read()
				
				try:
					ExchangeRate.currencies = pickle.loads(info)
				except:
					settings.log("Could not unpickle currencies file: " + file_name)
					file.close()
					os.remove(file_name)
					ExchangeRate.currencies = {}
			except:
				settings.log("Could not open currencies file:" + file_name)
				ExchangeRate.currencies = {}
		
		if not file == None:
			file.close()
		
		if ExchangeRate.currencies == None:
			ExchangeRate.currencies = {}
			
		amt_f = 0
		e = None
		if ExchangeRate.currencies.has_key(currency):
			e = ExchangeRate.currencies[currency]
		else:
			settings.log("Currency not found, sales report will be inaccurate!")
			settings.display_error("Currency rate for " + currency + " not found, sales report will be inaccurate. Please refresh and restart!")
			e = ExchangeRate(currency, 1.0, datetime.date.today() - datetime.timedelta(days=7))
			ExchangeRate.currencies[currency] = e
				
		return e
		
def convert_currency_to_usd(amount, amount_currency):
	# Will convert from this currency to USD. If the conversion
	# Value does not exist, it will update it from yahoo currencies
	
	if amount_currency == "USD":
		return amount
	
	exchange_rate = ExchangeRate.get(currency=amount_currency)
	if exchange_rate is None:
		return 0
			
	final_sum = exchange_rate.fraction_of_1_usd * amount 
	return final_sum  

def download_exchange_rate(currency):
	settings.log("Downloading currency: " + currency)
	url = "http://download.finance.yahoo.com/d/quotes.csv?s=" + currency + "USD=X&f=l1"
	import urllib2
	req = urllib2.Request(url=url)
	response = urllib2.urlopen(req)
	data = response.read()
	return float(data)

def download_all_currencies():
	ExchangeRate.preLoad = True
	
	ExchangeRate.get("USD")
	ExchangeRate.get("EUR")
	ExchangeRate.get("AED")
	ExchangeRate.get("AFN")
	ExchangeRate.get("ALL")
	ExchangeRate.get("AMD")
	ExchangeRate.get("ANG")
	ExchangeRate.get("AOA")
	ExchangeRate.get("ARS")
	ExchangeRate.get("AUD")
	ExchangeRate.get("AWG")
	ExchangeRate.get("AZN")
	ExchangeRate.get("BAM")
	ExchangeRate.get("BBD")
	ExchangeRate.get("BDT")
	ExchangeRate.get("BGN")
	ExchangeRate.get("BHD")
	ExchangeRate.get("BIF")
	ExchangeRate.get("BMD")
	ExchangeRate.get("BND")
	ExchangeRate.get("BOB")
	ExchangeRate.get("BOV")
	ExchangeRate.get("BRL")
	ExchangeRate.get("BSD")
	ExchangeRate.get("BTN")
	ExchangeRate.get("BWP")
	ExchangeRate.get("BYR")
	ExchangeRate.get("BZD")
	ExchangeRate.get("CAD")
	ExchangeRate.get("CDF")
	ExchangeRate.get("CHE")
	ExchangeRate.get("CHF")
	ExchangeRate.get("CHW")
	ExchangeRate.get("CLF")
	ExchangeRate.get("CLP")
	ExchangeRate.get("CNY")
	ExchangeRate.get("COP")
	ExchangeRate.get("COU")
	ExchangeRate.get("CRC")
	ExchangeRate.get("CUC")
	ExchangeRate.get("CUP")
	ExchangeRate.get("CVE")
	ExchangeRate.get("CZK")
	ExchangeRate.get("DJF")
	ExchangeRate.get("DKK")
	ExchangeRate.get("DOP")
	ExchangeRate.get("DZD")
	ExchangeRate.get("EEK")
	ExchangeRate.get("EGP")
	ExchangeRate.get("ERN")
	ExchangeRate.get("ETB")
	ExchangeRate.get("EUR")
	ExchangeRate.get("FJD")
	ExchangeRate.get("FKP")
	ExchangeRate.get("GBP")
	ExchangeRate.get("GEL")
	ExchangeRate.get("GHS")
	ExchangeRate.get("GIP")
	ExchangeRate.get("GMD")
	ExchangeRate.get("GNF")
	ExchangeRate.get("GTQ")
	ExchangeRate.get("GYD")
	ExchangeRate.get("HKD")
	ExchangeRate.get("HNL")
	ExchangeRate.get("HRK")
	ExchangeRate.get("HTG")
	ExchangeRate.get("HUF")
	ExchangeRate.get("IDR")
	ExchangeRate.get("ILS")
	ExchangeRate.get("INR")
	ExchangeRate.get("IQD")
	ExchangeRate.get("IRR")
	ExchangeRate.get("ISK")
	ExchangeRate.get("JMD")
	ExchangeRate.get("JOD")
	ExchangeRate.get("JPY")
	ExchangeRate.get("KES")
	ExchangeRate.get("KGS")
	ExchangeRate.get("KHR")
	ExchangeRate.get("KMF")
	ExchangeRate.get("KPW")
	ExchangeRate.get("KRW")
	ExchangeRate.get("KWD")
	ExchangeRate.get("KYD")
	ExchangeRate.get("KZT")
	ExchangeRate.get("LAK")
	ExchangeRate.get("LBP")
	ExchangeRate.get("LKR")
	ExchangeRate.get("LRD")
	ExchangeRate.get("LSL")
	ExchangeRate.get("LTL")
	ExchangeRate.get("LVL")
	ExchangeRate.get("LYD")
	ExchangeRate.get("MAD")
	ExchangeRate.get("MDL")
	ExchangeRate.get("MGA")
	ExchangeRate.get("MKD")
	ExchangeRate.get("MMK")
	ExchangeRate.get("MNT")
	ExchangeRate.get("MOP")
	ExchangeRate.get("MRO")
	ExchangeRate.get("MUR")
	ExchangeRate.get("MVR")
	ExchangeRate.get("MWK")
	ExchangeRate.get("MXN")
	ExchangeRate.get("MXV")
	ExchangeRate.get("MYR")
	ExchangeRate.get("MZN")
	ExchangeRate.get("NAD")
	ExchangeRate.get("NGN")
	ExchangeRate.get("NIO")
	ExchangeRate.get("NOK")
	ExchangeRate.get("NPR")
	ExchangeRate.get("NZD")
	ExchangeRate.get("OMR")
	ExchangeRate.get("PAB")
	ExchangeRate.get("PEN")
	ExchangeRate.get("PGK")
	ExchangeRate.get("PHP")
	ExchangeRate.get("PKR")
	ExchangeRate.get("PLN")
	ExchangeRate.get("PYG")
	ExchangeRate.get("QAR")
	ExchangeRate.get("RON")
	ExchangeRate.get("RSD")
	ExchangeRate.get("RUB")
	ExchangeRate.get("RWF")
	ExchangeRate.get("SAR")
	ExchangeRate.get("SBD")
	ExchangeRate.get("SCR")
	ExchangeRate.get("SDG")
	ExchangeRate.get("SEK")
	ExchangeRate.get("SGD")
	ExchangeRate.get("SHP")
	ExchangeRate.get("SLL")
	ExchangeRate.get("SOS")
	ExchangeRate.get("SRD")
	ExchangeRate.get("STD")
	ExchangeRate.get("SYP")
	ExchangeRate.get("SZL")
	ExchangeRate.get("THB")
	ExchangeRate.get("TJS")
	ExchangeRate.get("TMT")
	ExchangeRate.get("TND")
	ExchangeRate.get("TOP")
	ExchangeRate.get("TRY")
	ExchangeRate.get("TTD")
	ExchangeRate.get("TWD")
	ExchangeRate.get("TZS")
	ExchangeRate.get("UAH")
	ExchangeRate.get("UGX")
	ExchangeRate.get("USD")
	ExchangeRate.get("USN")
	ExchangeRate.get("USS")
	ExchangeRate.get("UYU")
	ExchangeRate.get("UZS")
	ExchangeRate.get("VEF")
	ExchangeRate.get("VND")
	ExchangeRate.get("VUV")
	ExchangeRate.get("WST")
	ExchangeRate.get("XAF")
	ExchangeRate.get("XAG")
	ExchangeRate.get("XAU")
	ExchangeRate.get("XBA")
	ExchangeRate.get("XBB")
	ExchangeRate.get("XBC")
	ExchangeRate.get("XBD")
	ExchangeRate.get("XCD")
	ExchangeRate.get("XDR")
	ExchangeRate.get("XFU")
	ExchangeRate.get("XOF")
	ExchangeRate.get("XPD")
	ExchangeRate.get("XPF")
	ExchangeRate.get("XPT")
	ExchangeRate.get("XTS")
	ExchangeRate.get("XXX")
	ExchangeRate.get("YER")
	ExchangeRate.get("ZAR")
	ExchangeRate.get("ZMK")
	ExchangeRate.get("ZWL")
	
	ExchangeRate.update_currencies()
	ExchangeRate.save_currencies()