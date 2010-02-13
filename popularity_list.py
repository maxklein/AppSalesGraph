# AppSalesGraph: AppStore Sales Graphing
# Copyright (c) 2010 by Max Klein (maximusklein@gmail.com)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
 

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
            