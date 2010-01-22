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


class AddEventDialog(wx.Dialog):
    def __init__(self, parent):
        super(AddEventDialog, self).__init__(parent, title="Add new event")

        sizer = wx.BoxSizer(wx.VERTICAL)

        box = wx.FlexGridSizer(2, 2)

        box.Add(
            wx.StaticText(self, -1, "Date:"), 0, wx.ALIGN_RIGHT|wx.ALL, 5)
        self.date = wx.DatePickerCtrl(
            self, size=(120, -1), style=wx.DP_DEFAULT, name="Event date")
        box.Add(self.date, 1, wx.ALIGN_LEFT|wx.ALL, 5)

        box.Add(
            wx.StaticText(self, -1, "Text:"), 0, wx.ALIGN_RIGHT|wx.ALL, 5)
        self.text = wx.TextCtrl(self, size=(120, -1))
        box.Add(self.text, 1, wx.ALIGN_LEFT|wx.ALL, 5)

        btnsizer = wx.StdDialogButtonSizer()

        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.AddMany((
            (box, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5),
            (btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)))
        
        self.SetSizerAndFit(sizer)
        
