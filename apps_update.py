# AppSalesGraph: AppStore Sales Graphing
# Copyright (c) 2010 by Max Klein (maximusklein@gmail.com)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

import os
import re
import time
import sys
import urllib2
from threading import Thread
from BeautifulSoup import BeautifulSoup	 
import xml.sax
import pprint 
import urllib
import appdailysales
import wx
import settings

from result_event  import ResultEvent

from app_info import AppInfoParser

		
class SalesDownloader(Thread):
	def __init__(self, notify_window, days_to_download):
		
		self.notify_window = notify_window
		self.days_to_download = days_to_download
		self.shutdown = False
		
		Thread.__init__(self)
		
	def requestShutdown(self):
		print "Requesting download thread shutdown"
		appdailysales.shutDownSalesDownload = True
		self.shutdown = True
		
	def run(self):
		
		if settings.DOWNLOAD_SALES:
			options = appdailysales.ReportOptions()
			options.appleId = settings.APPLE_ID
			options.password = settings.APPLE_PW
	  		options.outputDirectory = settings.SalesDir()
	  		options.unzipFile = True
	  		options.verbose = True
			options.daysToDownload = 7
			
			try:
			     filename, err = appdailysales.downloadFile(options, self.notify_window, self.days_to_download)
	  	  	except:
	  	  		filename = []
	  	  		wx.PostEvent(self.notify_window, ResultEvent("SalesDownloadError: Could not retrieve sales"))
	  	  		return
	  	  	
	  	  	if self.shutdown == True:
	  	  		print "Exiting download thread"
	  	  		return
	  	  	
	  	  	if err == True:
	  	  		return
	  	  	  
	  	  	self.filenames = filename
	  	  	  
	  		if len(filename) == 0:
	  			wx.PostEvent(self.notify_window, ResultEvent("SalesDownloadCompleteNoFiles"))
	  		else:
	  			wx.PostEvent(self.notify_window, ResultEvent("SalesDownloadComplete: Done: " + str(len(filename)) + " new reports!"))
	  	else:
	  		print "Sales download is disabled"
	  	 	wx.PostEvent(self.notify_window, ResultEvent("SalesDownloadCompleteNoFiles"))
	  
	
class UpdateDownloader(Thread):
   def __init__ (self, product_ids, notify_window):
	  self.product_ids = product_ids
	  self.notify_window = notify_window
	  self.reviews = {}
	  self.shutdown = False
	  
	  Thread.__init__(self)
	 
   def requestShutdown(self):
   	print "Review thread shutdown request"
   	self.shutdown = True
   	
   def run(self):
		print "Loading Data"
	
		for i, product_id in enumerate(self.product_ids):
			
			if self.shutdown == True:
	  	  		print "Exiting review download thread"
	  	  		return
	  	  	
			if settings.DOWNLOAD_REVIEWS == True:
				if self.shutdown == True:
	  	  		    print "Exiting review download thread"
	  	  		    return
	  	  	
				# print "Retrieving App Number" + i.__str__() + " with id=" + product_id.__str__()
				try:
					itunes7_useragent = "iTunes/4.2 (Macintosh; U; PPC Mac OS X 10.2"

					headers = {
                        "X-Apple-Tz" : "7200",
        	          	"Accept-Language" : "en-us, en;q=0.50",
        	          	"Connection" : "close",
        	          	"Host" : "ax.phobos.apple.com.edgesuite.net"
                   	    }
 
					request  = urllib2.Request('http://ax.phobos.apple.com.edgesuite.net/WebObjects/MZStore.woa/wa/viewContentsUserReviews?id=' + product_id.__str__() + '&pageNumber=0&sortOrdering=2&type=Purple+Software', None, headers)
					opener = urllib2.build_opener()
					opener.addheaders = [('User-agent', itunes7_useragent)]     
					
					fp = opener.open(request)

					html = fp.read()
				except:
					continue
				
				try:
					os.mkdir(settings.SalesDir("xml"))
				except:
					pass
				
				f = open(settings.SalesDir("xml/") + product_id.__str__() + ".xml", "w+")
				f.write(html)
				f.close()
			
			try:
				f = open(settings.SalesDir("xml/") + product_id.__str__() + ".xml", "r+")
			except:
				continue
			
			if self.shutdown == True:
	  	  		print "Exiting review download thread"
	  	  		return
	  	  	
			parser = xml.sax.make_parser()
			handler = AppInfoParser()
			parser.setContentHandler(handler)
			parser.parse(settings.SalesDir("xml/") + product_id.__str__() + ".xml")
			
			self.reviews[product_id] = handler.reviews
			
			image = urllib.URLopener()
			image.retrieve(handler.image_url, settings.DataDir("images/forapps/") + product_id.__str__() + ".jpg")
			
			try:
				wx.PostEvent(self.notify_window, ResultEvent("RefreshImageAndReviews:" + str(product_id)))
			except:
				pass
	
			
		from currency import ExchangeRate
		ExchangeRate.update_currencies()
        
		print "Image & Review Download Complete"
		
		wx.PostEvent(self.notify_window, ResultEvent("ReviewDownloadComplete"))
		