#!/usr/bin/python
#
# appdailysales.py
#
# iTune Connect Daily Sales Reports Downloader
# Copyright 2008-2009 Kirby Turner
#
# Version 1.9
#
# Latest version and additional information available at:
#   http://appdailysales.googlecode.com/
#
#
# This script will download yesterday's daily sales report from
# the iTunes Connect web site.  The downloaded file is stored
# in the same directory containing the script file.  Note: if
# the download file already exists then it will be overwritten.
#
# The iTunes Connect web site has dynamic urls and form field
# names.  In other words, these values change from session to
# session.  So to get to the download file we must navigate  
# the site and webscrape the pages.  Joy, joy.
#
#
# Contributors:
#   Leon Ho
#   Rogue Amoeba Software, LLC
#   Keith Simmons
#   Andrew de los Reyes
#   Maarten Billemont
#   Max Klein
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


# -- Change the following to match your credentials --
# -- or use the command line options.               --
appleId = 'Your Apple Id' 
password = 'Your Password'
outputDirectory = ''
unzipFile = False
verbose = False
daysToDownload = 1
dateToDownload = None
# ----------------------------------------------------


import urllib
import urllib2
import cookielib
import datetime
import re
import getopt
import sys
import os
import gzip
import StringIO
import traceback
import wx
from result_event  import ResultEvent

shutDownSalesDownload = False

try:
    import BeautifulSoup
except ImportError:
    BeautifulSoup = None


class ITCException(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value);

# The class ReportOptions defines a structure for passing
# report options to the download routine. The expected
# data attributes are:
#   appleId
#   password
#   outputDirectory
#   unzipFile
#   verbose
#   daysToDownload
# Note that the class attributes will default to the global
# variable value equivalent.
class ReportOptions:
    def __getattr__(self, attrname):
        if attrname == 'appleId':
            return appleId
        elif attrname == 'password':
            return password
        elif attrname == 'outputDirectory':
            return outputDirectory
        elif attrname == 'unzipFile':
            return unzipFile
        elif attrname == 'verbose':
            return verbose
        elif attrname == 'daysToDownload':
            return daysToDownload
        elif attrname == 'dateToDownload':
            return dateToDownload
        else:
            raise AttributeError, attrname



# There is an issue with Python 2.5 where it assumes the 'version'
# cookie value is always interger.  However, itunesconnect.apple.com
# returns this value as a string, i.e., "1" instead of 1.  Because
# of this we need a workaround that "fixes" the version field.
#
# More information at: http://bugs.python.org/issue3924


class MyCookieJar(cookielib.CookieJar):
    def _cookie_from_cookie_tuple(self, tup, request):
        name, value, standard, rest = tup
        version = standard.get('version', None)
        if version is not None:
            version = version.replace('"', '')
            standard["version"] = version
        return cookielib.CookieJar._cookie_from_cookie_tuple(self, tup, request)


def showCookies(cj):
    for index, cookie in enumerate(cj):
        print index, ' : ', cookie
    

def readHtml(opener, url, data=None):
    request = urllib2.Request(url, data)
    urlHandle = opener.open(request)
    html = urlHandle.read()
    return html


def downloadFile(options, notify_window, days_to_download):
    #if options.verbose == True:
    
    global shutDownSalesDownload
    
    wx.PostEvent(notify_window, ResultEvent("Connecting..."))
        # print '-- begin script --'
    
    urlBase = 'https://itts.apple.com%s'

    cj = MyCookieJar();
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    if shutDownSalesDownload == True: return
    
    # Go to the iTunes Connect website and retrieve the
    # form action for logging into the site.
    urlWebsite = urlBase % '/cgi-bin/WebObjects/Piano.woa'
    html = readHtml(opener, urlWebsite)
    match = re.search('" action="(.*)"', html)
    urlActionLogin = urlBase % match.group(1)

    if shutDownSalesDownload == True: return None, None
    wx.PostEvent(notify_window, ResultEvent("Connected! Logging in..."))
    
    # Login to iTunes Connect web site and go to the sales 
    # report page, get the form action url and form fields.  
    # Note the sales report page will actually load a blank 
    # page that redirects to the static URL. Best guess here 
    # is that the server is setting some session variables 
    # or something.
    webFormLoginData = urllib.urlencode({'theAccountName':options.appleId, 'theAccountPW':options.password, '1.Continue.x':'0', '1.Continue.y':'0'})
    html = readHtml(opener, urlActionLogin, webFormLoginData)
    
    html_lc = html.lower()
    if html_lc.find("piano-sign in") > 0:
        wx.PostEvent(notify_window, ResultEvent("SalesDownloadError: Could not login"))
        return [], True
    
    if html_lc.find("checkvendoridnumber") > 0:
        # Oh, oh, we have a multiple vendor login
        
        soup = BeautifulSoup.BeautifulSoup( html )
        
        # Let's get all vendor IDs
        selectField = soup.find( 'select', attrs={'id': 'selectName'} )
        html_options = selectField.findAll('option')
        for option in html_options:
            val = option['value']
            if val == "0": continue
            
            # Get the url to post to
            form = soup.find( 'form', attrs={'name': 'superPage' } )
            urlSelectVendor = urlBase % form['action']
            wosid1 = soup.find( 'input', attrs={'name': 'wosid'} )['value']
            # countryName = soup.find( 'input', attrs={'id': 'hiddenCountryName'} )['value']
            
            # This is fragile. It should be parsed from the html
            vendorSelectData = urllib.urlencode({'vndrid': val, 'wosid':wosid1, '9.6.0':val, '9.18':"", 'SubmitBtn':'Submit'})
            
            html = readHtml(opener, urlSelectVendor, vendorSelectData)
            
            if html.find("selDateType") > 0:
                # Looks like we found the page
                html_lc = html.lower()
                break
            break # Let's just do first vendor for now

        if html.find("selDateType") <= 0:
            # Page was not opened
            wx.PostEvent(notify_window, ResultEvent("SalesDownloadError: Multiple Vendors not supported"))
            return [], True
            
    if shutDownSalesDownload == True: return None, None
    
    # Get the form field names needed to download the report.
    successfully_parsed = False
    if BeautifulSoup:
        # if options.verbose == True:
        wx.PostEvent(notify_window, ResultEvent("Logged in! Accessing sales data"))
            
            # print 'using BeautifulSoap for HTML parsing'
        try:
            soup = BeautifulSoup.BeautifulSoup( html )
            # print html
            
            form = soup.find( 'form', attrs={'name': 'frmVendorPage' } )
        
            try:
                urlDownload = urlBase % form['action']
            except TypeError:
                if html.find("Session Time Out") != -1:
                    wx.PostEvent(notify_window, ResultEvent("Session timeout"))
                else:
                    wx.PostEvent(notify_window, ResultEvent("Invalid Data Returned. Try again later."))
                return
        
            fieldNameReportType = soup.find( 'select', attrs={'id': 'selReportType'} )['name']
            fieldNameReportPeriod = soup.find( 'select', attrs={'id': 'selDateType'} )['name']
            fieldNameDayOrWeekSelection = soup.find( 'input', attrs={'name': 'hiddenDayOrWeekSelection'} )['name'] #This is kinda redundant
            fieldNameSubmitTypeName = soup.find( 'input', attrs={'name': 'hiddenSubmitTypeName'} )['name'] #This is kinda redundant, too
            successfully_parsed = True
        except:
            pass
        

   
    if successfully_parsed == False:
        match = re.findall('name="frmVendorPage" action="(.*)"', html)
        urlDownload = urlBase % match[0]
        match = re.findall('name="(.*?)"', html)
        fieldNameReportType = match[4] # selReportType
        fieldNameReportPeriod = match[5] # selDateType
        fieldNameDayOrWeekSelection = match[8] # hiddenDayOrWeekSelection
        fieldNameSubmitTypeName = match[9] # hiddenSubmitTypeName

    
    wx.PostEvent(notify_window, ResultEvent("Requesting daily sales..."))
    
    if shutDownSalesDownload == True: return None, None
    
    # Ah...more fun.  We need to post the page with the form
    # fields collected so far.  This will give us the remaining
    # form fields needed to get the download file.
    webFormSalesReportData = urllib.urlencode({fieldNameReportType:'Summary', fieldNameReportPeriod:'Daily', fieldNameDayOrWeekSelection:'Daily', fieldNameSubmitTypeName:'ShowDropDown'})
    html = readHtml(opener, urlDownload, webFormSalesReportData)

    if shutDownSalesDownload == True: return None, None
    
    if BeautifulSoup:
        soup = BeautifulSoup.BeautifulSoup( html )
        form = soup.find( 'form', attrs={'name': 'frmVendorPage' } )
        try:
            urlDownload = urlBase % form['action']
        except TypeError:
            wx.PostEvent(notify_window, ResultEvent("Invalid Data Returned. Try again later."))
            return
        
        select = soup.find( 'select', attrs={'id': 'dayorweekdropdown'} )
        fieldNameDayOrWeekDropdown = select['name']
    else:
        match = re.findall('name="frmVendorPage" action="(.*)"', html)
        urlDownload = urlBase % match[0]
        match = re.findall('name="(.*?)"', html)
        fieldNameDayOrWeekDropdown = match[6]

    # Set the list of report dates.
    reportDates = []
    if not days_to_download == None:
        for a_day in days_to_download:
            date = '%02i/%02i/%i' % (a_day.month, a_day.day, a_day.year)
            reportDates.append( date )
    else:
        if options.dateToDownload == None:
            for i in range(int(options.daysToDownload)):
                today = datetime.date.today() - datetime.timedelta(i + 1)
                date = '%02i/%02i/%i' % (today.month, today.day, today.year)
                reportDates.append( date )
        else:
            reportDates = [options.dateToDownload]
        
    if options.verbose == True:
        wx.PostEvent(notify_window, ResultEvent("Retrieving for dates:" + reportDates.__str__()))
        
        # print 'reportDates: ', reportDates

    unavailableCount = 0
    filenames = []
    for downloadReportDate in reportDates:
        wx.PostEvent(notify_window, ResultEvent("Requesting: " + downloadReportDate))
        
        if shutDownSalesDownload == True: return None, None
        
        # And finally...we're ready to download yesterday's sales report.
        webFormSalesReportData = urllib.urlencode({fieldNameReportType:'Summary', fieldNameReportPeriod:'Daily', fieldNameDayOrWeekDropdown:downloadReportDate, 'download':'Download', fieldNameDayOrWeekSelection:downloadReportDate, fieldNameSubmitTypeName:'Download'})
        urlHandle = opener.open(urlDownload, webFormSalesReportData)
        try:
            if shutDownSalesDownload == True: return None, None
            
            filename = urlHandle.info().getheader('content-disposition').split('=')[1]
            
            # For some reason, there are geese feet on the filename
            filename = filename.replace("'", "")
            filename = filename.replace("\"", "")
            
            # filesize = urlHandle.info().getheader('size')
            # wx.PostEvent(notify_window, ResultEvent("Getting Sales: " + downloadReportDate + " (" + filesize + ")"))
            
            filebuffer = urlHandle.read()
            urlHandle.close()

            if options.unzipFile == True:
                if options.verbose == True:
                    wx.PostEvent(notify_window, ResultEvent("Unzipping:" + filename))
                    # print 'unzipping archive file: ', filename
                #Use GzipFile to de-gzip the data
                ioBuffer = StringIO.StringIO( filebuffer )
                gzipIO = gzip.GzipFile( 'rb', fileobj=ioBuffer )
                filebuffer = gzipIO.read()

            filename = os.path.join(options.outputDirectory, filename)
            if options.unzipFile == True and filename[-3:] == '.gz': #Chop off .gz extension if not needed
                filename = os.path.splitext( filename )[0]

            if options.verbose == True:
                print 'saving download file:', filename

            downloadFile = open(filename, 'w')
            downloadFile.write(filebuffer)
            downloadFile.close()

            filenames.append( filename )
        except AttributeError:
            wx.PostEvent(notify_window, ResultEvent('%s report is not available - try again later.' % downloadReportDate))
            # print '%s report is not available - try again later.' % downloadReportDate
            unavailableCount += 1

    # if unavailableCount > 0:
    #    raise ITCException, '%i report(s) not available - try again later' % unavailableCount

    if options.verbose == True:
        wx.PostEvent(notify_window, ResultEvent("Sales Report Download Complete"))

    return filenames, False
