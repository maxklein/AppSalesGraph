# AppSalesGraph: AppStore Sales Graphing
# Copyright (c) 2010 by Max Klein (maximusklein@gmail.com)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
 

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
        
