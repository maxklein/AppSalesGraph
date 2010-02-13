# AppSalesGraph: AppStore Sales Graphing
# Copyright (c) 2010 by Max Klein (maximusklein@gmail.com)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
 


import csv, datetime, heapq, itertools, matplotlib, operator, os, wx, wxmpl
import random, sys, locale
import matplotlib.dates as mdates
import wx.lib.masked as masked
import    wx.lib.mixins.listctrl    as    listmix
from collections import defaultdict
from currency import convert_currency_to_usd
from app_info import AppInfoParser
import xml.sax
from apps_update import SalesDownloader

import time
from datetime import timedelta

import settings


class PlotPanel(wxmpl.PlotPanel):
    title = None
    has_graphics = True
    sales_period = None
    displayCurrency = False
    
    def __init__(self, parent):
        super(PlotPanel, self).__init__(
            parent, -1, cursor=False, location=False, crosshairs=False,
            selection=False, zoom=False)
        
        # self.SetWindowStyle(self.GetWindowStyle()|wx.NO_BORDER)
        
        self.colors = defaultdict(
            lambda: [random.random(), random.random(), random.random()])
        
        self.figure = self.get_figure()
        # self.figure.set_frameon(False)
        self.figure.set_edgecolor('white')
        self.figure.set_facecolor('white')
        # self.figure.set_linewidth(0)
        
        self.figure.subplots_adjust(
            hspace=0.2, left=0.05, top=0.95, right=0.95, bottom=0.05)

        self.panel = parent.GetParent()
        self.figure.clear()
        self.axes2 = self.figure.add_subplot(211)
        self.axes1 = self.figure.add_subplot(212)

    def Update(self):
        self.axes1.clear()
        #self.axes1.set_title("Sales Line Chart")
        self.axes2.clear()
        #self.axes2.set_title("Sales Bar Chart")

        date_range = self.panel.date_range.GetValue()
        product_ids = self.panel.selected_products

        show_sum = product_ids == [None]
        prefix = "sum_" if show_sum else ""
        product_data = getattr(
            self.panel.sales_period,
            '%s%s_sales' % (prefix,
                            ('daily' if date_range <= settings.DAYS_TO_SHOW else 'weekly')))
        
        # product_data = self.sales_period.daily_sales
        limits = self.panel.GetDateLimits()
        num_start, num_end = map(mdates.date2num, limits)

        total = len(product_ids)
        if total:
            bar_width = 1.0 / total

        # this is the name of the attribute like "amount" or "sales"
        value_getter = self.panel.graph_renderer
        max_value = None

        values = []

        # loop through all products
        for i, product_id in enumerate(product_ids):
            dates = [] # dictionary for dates, which is the horizontal axis
            values = [] # dictionary for the values
            
            # get the data for all or for a single product
            data = product_data.get(product_id, {}) if product_id else product_data

            last_date = None
            
            # loop through all the "Event" objects that have our sales data
            for event_date, event in data.iteritems():
                
                # numstart is the start of the date range we are interested in. The
                # Event object has a comparison function defined, so we look if the
                # object is within the range we are interested in
                if event >= num_start:
                    if last_date != event.end_num - 1:
                        if last_date:
                            dates.append(last_date + 1)
                            values.append(0)
                        
                        # Get the dates in the array
                        dates.append(event.end_num - 1)
                        values.append(0)
                    last_date = event.end_num
                    
                    if event <= num_end:
                        # print event
                        val = value_getter(event)
                        # print val
                        # if val > 0:
                        dates.append(event.end_num)
                        
                        # Get the value we want and put it in the dictionary
                        # value_getter(event) = self.panel.graph_renderer, which
                        # is operator.attrgetter('sales'). It gets the 'sales'
                        # variable from the event object. 
                        # print val
                        values.append(val)
                        
            else:
                if last_date:
                    dates.append(last_date + 1)
                    values.append(0)
            
            self.axes1.plot(
                dates, values, 'o-', color=self.colors[product_id])

            bar_dates, bar_values = [], []
            for date, value in itertools.izip(dates, values):
                if value:
                    bar_dates.append(date)
                    bar_values.append(value)
                    # print "VAL: " + value.__str__()

            rects = self.axes2.bar(
                [date + i*bar_width - 0.5 for date in bar_dates],
                bar_values, width=bar_width, color=self.colors[product_id])
            # label=(self.panel.product_names[product_id])
            for rect in rects:
                height = rect.get_height()
                
                if PlotPanel.displayCurrency:
                    self.axes2.text(rect.get_x()+rect.get_width()/2., 1.06*height,
                                settings.format_currency(height), ha='center', va='bottom')
                else:
                      self.axes2.text(rect.get_x()+rect.get_width()/2., 1.06*height,
                                '%d' % int(height), ha='center', va='bottom')

        if values:
            max_value = max(values)
            # print "Max Value: " + max_value.__str__()
            
            for value, text in self.panel.event_levels:
                line = self.axes1.plot(
                    [value, value], [0, max_value], '--', color="red")
                self.axes2.plot(
                    [value - 0.5, value - 0.5], [0, max_value], '--',
                    color="red")
                self.axes2.text(value - 1, 1.01 * max_value, text)

        interval = (max(1, (date_range / settings.MAX_TICKS * 2)))
        major_locator = mdates.DayLocator(interval=interval)  # every month
        minor_locator = mdates.DayLocator()
        dateFmt = mdates.DateFormatter(settings.date_format)
        self.axes1.set_xlim(num_start - 1, num_end + 1)
        self.axes2.set_xlim(num_start - 0.5, num_end + 0.5)
        for axes in (self.axes1, self.axes2):
            axes.set_ylim(0, max_value)
            axes.xaxis.set_major_locator(major_locator)
            axes.xaxis.set_major_formatter(dateFmt)
            axes.xaxis.set_minor_locator(minor_locator)
            axes.grid(True)
        self.draw()
