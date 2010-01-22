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
class ReviewsList(wx.ListCtrl):
    
    def __init__(self, parent):
        super(ReviewsList, self).__init__(parent, style=wx.LC_REPORT)
        
        # self.reviews = [{"Text" : "This is the first review", "Reviewer" : "Mark", "Stars" : 5}]
        self.panel = parent.GetParent()
        self.InsertColumn(0, 'Review Text', 300)
        self.InsertColumn(1, 'Reviewer Name')
        self.InsertColumn(2, 'Stars')
        
        self.SetColumnWidth(0, 300)
        self.SetColumnWidth(1, 100)
        self.SetColumnWidth(2, 70)
        

    def setReviews(self, reviews):
        
        self.DeleteAllItems()
        for i, review_dict in enumerate(reviews):
            # .decode('iso-8859-1')
            index = self.InsertStringItem(i, review_dict['ReviewBody'].decode('utf-8'))
            self.SetStringItem(index, 1, review_dict['ReviewHeader'])
            # self.SetStringItem(index, 2, str(review_dict['Stars']))