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
import settings

# Reviews Listview
class PopularityList(wx.ListCtrl):
    
    def __init__(self, parent):
        super(PopularityList, self).__init__(parent, style=wx.LC_REPORT)
        
        # self.reviews = [{"Text" : "This is the first review", "Reviewer" : "Mark", "Stars" : 5}]
        self.panel = parent.GetParent()
        self.InsertColumn(0, '#')
        self.InsertColumn(1, 'App Name')
        self.InsertColumn(2, 'Last Sale')
        self.InsertColumn(3, 'Downloads')
        
        # self.SetColumnWidth(0, 300)
        # self.SetColumnWidth(1, 100)
        # self.SetColumnWidth(2, 70)
     
            

    def SetData(self, sales_period):

        self.DeleteAllItems()
        
        date_to_view = sales_period.last_sales_day
        limits = (date_to_view, date_to_view)
        
        product_ids = sales_period.productIdsSorted(ByPopularity=True)
        
        pop = 1
        for product_id in product_ids:
            product_name = sales_period.product_names[product_id]
            revenue, cnt = sales_period.downloadsForProductOnLastReport(product_id, limits)
            
            index = self.InsertStringItem(pop, str(pop))
            self.SetStringItem(index, 1, product_name)
            self.SetStringItem(index, 2, revenue)
            self.SetStringItem(index, 3, str(cnt))
            pop = pop + 1
            