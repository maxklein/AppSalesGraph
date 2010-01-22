# AppSalesGraph: AppStore Sales Graphing
# Copyright (c) 2010 by Max Klein (maximusklein@gmail.com)
#
# GNU General Public Licence (GPL)
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#


import wx
import wx.lib.mixins.listctrl as listmix
import settings
import matplotlib.dates as mdates

# Sales Listview
class SalesListCtrl(wx.ListCtrl):
    has_graphics = False
    
    def __init__(self, parent):
        super(SalesListCtrl, self).__init__(parent, style=wx.LC_REPORT)
        self.panel = parent.GetParent()
        self.InsertColumn(0, 'Name')
        self.InsertColumn(1, 'Date')
        self.InsertColumn(2, 'Amount')
        self.InsertColumn(3, 'Profit')
        self.InsertColumn(4, 'Country')
      
        
    def Update(self):
        return
        
        self.DeleteAllItems()

        product_ids = self.panel.selected_products
        date_range = self.panel.date_range.GetValue()

        show_sum = product_ids == [None]
        prefix = "sum_" if show_sum else ""
        product_data = getattr(
            self.panel.sales_period,
            '%s%s_sales' % (prefix,
                            ('daily' if date_range <= settings.DAYS_TO_SHOW else 'weekly')))

        limits = self.panel.GetDateLimits()
        num_start, num_end = map(mdates.date2num, limits)

        for i, product_id in enumerate(product_ids):
            data = product_data if show_sum else product_data[product_id]
            for pos, event in enumerate(data):
                if event >= num_start:
                    if event <= num_end:
                        index = self.InsertStringItem(pos, event.name)
                        self.SetStringItem(
                            index, 1, event.end_date.strftime(settings.date_format))
                        self.SetStringItem(index, 2, str(event.sales))
                        self.SetStringItem(
                            index, 3, event.currency + str(event.total_price))
                        self.SetStringItem(index, 4, event.country)

    