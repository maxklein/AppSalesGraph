# AppSalesGraph: AppStore Sales Graphing
# Copyright (c) 2010 by Max Klein (maximusklein@gmail.com)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.


 
from currency      import convert_currency_to_usd
from UnicodeReader import UnicodeReader
from matplotlib    import dates as mdates
from collections   import defaultdict
from datetime      import timedelta
from threading     import Thread
from result_event  import ResultEvent
from app_info      import AppInfoParser

import csv, heapq, os, time, datetime, itertools, operator, settings, wx, xml.sax

class SalesProcessorDialect(csv.excel):
    delimiter = '\t'
    quoting = csv.QUOTE_NONE
    lineterminator = '\n'

csv.register_dialect('sales', SalesProcessorDialect)

class SalesPeriod(Thread):
    def __init__(self, notify_window):
        self.loaded_dates = [] # All the days loaded
        self.daily_sales = defaultdict(dict) # first dict is product_id, second dict is days mapped to events
        self.weekly_sales = defaultdict(dict)
        
        self.sum_daily_sales = defaultdict(dict)
        self.sum_weekly_sales = defaultdict(dict)
        self.unavailable_days = {}
        self.available_days = {}
        self.product_names = {}
        self.product_ids = []
        self.notify_window = notify_window
        self.reviews = defaultdict(list)
        self.last_sales_day = None
        self.shutdown = False
        
        Thread.__init__(self)
    
    def run(self):
        settings.log("Starting sales file load")
        
        self.addSalesFiles()
        if (self.shutdown == True): 
            settings.log("Sales Load Thread Ended")
            return
        
        self.refreshSalesData()
        if (self.shutdown == True):
            settings.log("Sales Load Thread Ended")
            return
        
        if self.notify_window != None:
            try:
                wx.PostEvent(self.notify_window, ResultEvent("SalesInfoRetrieved"))
            except:
                print "Main window shutdown. Sales Thread could not notify"
            
        settings.log("Sales Load Thread Ended")
    
    def loadReviews(self, product_id):
        try:
            f = open(settings.SalesDir("xml/") + product_id.__str__() + ".xml", "r+")
        except:
            return
             
        parser = xml.sax.make_parser()
        handler = AppInfoParser()
        parser.setContentHandler(handler)
        try:
            parser.parse(settings.SalesDir("xml/") + product_id.__str__() + ".xml")
        except:
            # fails if wrong xml in dir
            pass
        
        self.reviews[product_id] = handler.reviews
        
        f.close()
        
        
    def isDateAlreadyLoaded(self, filename):
        f = open(filename, "rb")
        reader = UnicodeReader(f, dialect='sales')
        
        for fields in reader:
            # This loop only runs once
            try:
                begin_date = fields['Begin Date']
            except:
                return False
            
            already_loaded = False
            
            for d in self.loaded_dates:
                if d == begin_date:
                    already_loaded = True
        
                    if already_loaded:
                        f.close()
                        return True
        
            self.loaded_dates.append(begin_date)
            break
        
        f.close()
        return False
    
    def requestShutdown(self):
        settings.log("Shutdown of sales thread requested")
        self.shutdown = True
        
    def addSalesFile(self, filename):
        if (os.path.isdir(filename)):
            return
        
        if (self.shutdown == True):
            return
    
        # Check if we already have data for this date
        if self.isDateAlreadyLoaded(filename):
            if settings.MOVE_DOUBLE_FILES:
                try:
                    dir = settings.SalesDir("double/")
                    os.makedirs(dir)
                except:
                    pass
    
                import shutil
                shutil.move(filename, settings.SalesDir("double/" + os.path.basename(filename)))
            return None
    
        f = open(filename, "rb")
        settings.log("Loading: " + filename)
        reader = UnicodeReader(f, dialect='sales')
        
        for fields in reader:
            try:
                if fields['Product Type Identifier'] == "7":
                    continue
            except:
                # If exception is thrown here, file invalid
                return
            
            if (self.shutdown == True): return
            
            begin_date = fields['Begin Date']
            end_date = fields['End Date']
            
            begin_month, begin_day, begin_year = map(int, begin_date.split('/'))
            product_begin_date = datetime.date(begin_year, begin_month, begin_day)
                
            end_month, end_day, end_year = map(int, end_date.split('/'))
            product_end_date = datetime.date(end_year, end_month, end_day)

            product_id = int(fields['Apple Identifier'])
            self.product_names[product_id] = unicode(fields['Title / Episode / Season'], "utf-8")       
            
            sales = (self.daily_sales if begin_date == end_date else self.weekly_sales)
            
            sale_date_found = False
            new_sale_event = SalesForProductOnDate()
            new_sale_event.init_with_fields(fields, product_end_date)
            
            product_sale_list = sales[product_id] # gets dictionary mapping date to sales object
            
            # Search if we already have this date
            for sale_date, sale_event in product_sale_list.iteritems():
                if sale_event.end_num == new_sale_event.end_num:
                    product_sale_list[sale_event.end_num].paid_downloads += new_sale_event.paid_downloads
                    
                    # Handles case that same product has two prices on same day
                    product_sale_list[sale_event.end_num].total_price += new_sale_event.price * new_sale_event.paid_downloads
                    sale_date_found = True
            
            if sale_date_found == False:
                product_sale_list[new_sale_event.end_num] = new_sale_event
                self.available_days[new_sale_event.end_date] = True
        try:
            if self.last_sales_day == None or self.last_sales_day < new_sale_event.end_date:
                self.last_sales_day = new_sale_event.end_date
        except:
            pass # this happens if file invalid

    def sumSales(self):
        
        self.sum_daily_sales = {}
        self.yesterday_summary = []
        
        # Look through weekly and daily
        for product_id, date_sale_dict in self.daily_sales.iteritems():
            for sale_date, sale_event in date_sale_dict.iteritems():
                
                if (self.shutdown == True): return
                
                # Looping through all dates for each product
                if self.sum_daily_sales.has_key(sale_date) == True:
                    sum_sale_event = self.sum_daily_sales[sale_date]
                else:
                    sum_sale_event = SalesForProductOnDate(product_id=None, name='All', company='Unknown', 
                                                           price=0.0, currency='Unknown', country='Unknown', 
                                                           paid_downloads=0, end_date=sale_event.end_date)
                    self.sum_daily_sales[sale_date] = sum_sale_event
                    
                sum_sale_event.paid_downloads += sale_event.paid_downloads
                sum_sale_event.total_price += sale_event.total_price
                
    def popSorter(self, item1, item2):
        
        date_to_view = self.last_sales_day
        limits = (date_to_view, date_to_view)
        
        rev1, cnt1 = self.downloadsForProductOnLastReport(item1, limits)
        rev2, cnt2 = self.downloadsForProductOnLastReport(item2, limits)
        
        if cnt1 == cnt2:
            return 0
        
        if cnt1 > cnt2:
            return -1
        
        return 1
       
    def productIdsSorted(self, ByPopularity=True, ByName=False):
        # Will return the list of item ids, but sorted
        product_ids = sorted(self.product_ids, cmp=self.popSorter)
        
        return product_ids
        
    def addSalesFiles(self):
        import glob
        date_file_list = []
        for file in glob.glob(settings.SalesDir("*.txt")):
            stats = os.stat(file)
            lastmod_date = time.localtime(stats[8])
            date_file_tuple = lastmod_date, file
            date_file_list.append(date_file_tuple)
        
        item_count = len(date_file_list)
        i = 1
        date_file_list.sort()
        for d, f in date_file_list:
            self.addSalesFile('%s' % f)
            
            wx.PostEvent(self.notify_window, ResultEvent("SalesFileLoaded: Loaded " + str(i) + " of " + str(item_count)))
            i = i + 1
                    
    def refreshSalesData(self):
        settings.log("Refreshing sales data")
                      
        self.sumSales()
        self.unavailable_days = {}
        
        for i in range(settings.DAYS_TO_CHECK):
            the_day = datetime.datetime.now().date() - timedelta(days=i)
            
            if self.available_days.has_key(the_day) == False:
                self.unavailable_days[the_day] = True
                
        # Now sort the product IDs with respect to their title.
        self.product_names_reverse = defaultdict(list)
        for id, title in self.product_names.iteritems():
            self.product_names_reverse[title].append(id)
        
        # What is this for?
        for title, ids in sorted(self.product_names_reverse.iteritems()):
            self.product_ids.extend(ids)
            self.loadReviews(ids[0])

    def revenueForRange(self, product_id, number_of_days):
        if len(self.available_days) == 0:
             return
        
        range = (datetime.date.today() - datetime.timedelta(number_of_days), datetime.date.today())
        num_start, num_end = map(mdates.date2num, range)
        
        total_revenue = 0
        if product_id == None:
            sales = self.sum_daily_sales
        else:
            sales = self.daily_sales[product_id]
            
        for date, sale_event in sales.iteritems():
            if date >= num_start and date <= num_end:
                total_revenue = total_revenue + sale_event.total_price
    
        return "Revenue for last " + number_of_days.__str__() + " days: " + settings.format_currency(total_revenue), total_revenue
    
    def averageRevenueForRange(self, product_id, number_of_days, sales_for_range):
        val = sales_for_range / number_of_days
        return "Daily Average (" + number_of_days.__str__() + " days): " + settings.format_currency(val)

            
    def downloadsForProductOnLastReport(self, product_id, date_range):
        if len(self.available_days) == 0:
             return None, None
        
        num_start, num_end = map(mdates.date2num, date_range)
        
        if product_id == None:
            all_sales = self.sum_daily_sales[num_end]
            return settings.format_currency(all_sales.total_price), all_sales.paid_downloads

        day_count = 0            
        total_sales = 0
        if product_id == None:
            product_id = self.product_ids[0]
    
        data = self.daily_sales[product_id]
        if data.has_key(num_end) == False:
            return settings.format_currency(0), 0
        
        sales_event = data[num_end]
        
        return settings.format_currency(sales_event.total_price), sales_event.paid_downloads
    
    def lastSales(self, product_id):
        if len(self.available_days) == 0:
             return "No sales ever"
            
        if product_id == None:
            product_id = self.product_ids[0]
        
        
        the_sale_event = None 
        revenue = 0
        highest_date = 0
        sales = self.daily_sales[product_id]
        for date, sale_event in sales.iteritems():
            if date > highest_date:
                highest_date = date
                the_sale_event = sale_event

        return "Last day with sales: " + settings.format_currency(sale_event.total_price) + " on " + str(sale_event.end_date.strftime(settings.date_format))
    
        
        
class SalesForProductOnDate(object):
    def __init__(self, product_id=None, name='All', company='Unknown', price=0.0,
        currency='Unknown', country='Unknown', paid_downloads=0, end_date=None):
        
        if end_date != None:
            self.end_num = mdates.date2num(end_date)
            
        self.end_date = end_date
        self.product_id = product_id
        self.name = name
        self.company = company
        self.price = price
        self.currency = currency
        self.country = country
        self.paid_downloads = paid_downloads
        self.total_price = self.price * self.paid_downloads
                
    def init_with_fields(self, fields, end_date):
        self.__init__(int(fields['Apple Identifier']), fields['Title / Episode / Season'],
            fields['Artist / Show'], convert_currency_to_usd(float(fields['Royalty Price']), fields['Customer Currency']),
            'USD', fields['Country Code'],
            int(fields['Units']), end_date)

    def __cmp__(self, other):
        return (
            cmp(self.end_num, other) if isinstance(other, float)
            else cmp(self.end_num, other.end_num))

    def __str__(self):
        return "%s:%s@%s" % (self.name, self.paid_downloads, self.end_date)

    __repr__ = __str__
    