# AppSalesGraph: AppStore Sales Graphing
# Copyright (c) 2010 by Max Klein (maximusklein@gmail.com)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
 

import wx
import settings

class SettingsDialog(wx.Dialog):
    def __init__(self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
                 style=wx.DEFAULT_DIALOG_STYLE):
        
        # super(SettingsDialog, self).__init__(parent, ID, title)
        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI object using the Create
        # method.
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)
 
        
        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate(pre)
        
        icon = wx.Icon("images/settings.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        
        # Create the labels on the left
        wx.StaticText(self, -1, "iTunes User Name:", pos=(1,33),  size=(70,30),
                      style=wx.ALIGN_RIGHT)

        wx.StaticText(self, -1, "iTunes Password:", pos=(1,73),size=(70,30),
                      style=wx.ALIGN_RIGHT)

        wx.StaticText(self, -1, "Sales Directory:", pos=(1,113),size=(70,30),
                      style=wx.ALIGN_RIGHT)
        
        self.text = wx.TextCtrl(self, -1, pos=(100,36),size=(180,20), value=settings.APPLE_ID)
        self.passw = wx.TextCtrl(self, -1, pos=(100,76),size=(180,20), style = wx.TE_PASSWORD, value=settings.APPLE_PW)
        self.sales_dir = wx.TextCtrl(self, -1, pos=(100,116),size=(100,20), value=settings.SALES_DIR)
        self.browse_btn = wx.Button(self, -1, "Select...", pos=(215,116))
        self.Bind(wx.EVT_BUTTON, self.OnBrowseForDir, self.browse_btn)
        
        # OK and Cancel Buttons
        btnOK = wx.Button(self, -1, "OK", pos=(160, 160), size=(70,30))
        btnOK.SetDefault()
        btnCancel = wx.Button(self, -1, "Cancel", pos=(235, 160), size=(70,30))
        self.Bind(wx.EVT_BUTTON, self.OnOK, btnOK)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, btnCancel)
        
        # Show
        # self.Show(True)
        # get access to the parent form and the parent settings
        # self.parent = parent
       # self.settings = parent.settings

        # initialize values
        # self.ctlDelay.SetValue(self.settings.slideshow_delay)    

    def OnBrowseForDir(self,event):
        dialog = wx.DirDialog(self, message = "Select the folder", style = 0)
        
        if dialog.ShowModal() == wx.ID_OK:
            self.sales_dir.SetValue(dialog.GetPath())
            
    def OnOK(self,event):
        """ OK Button Clicked """
        settings.APPLE_ID = self.text.GetValue()
        settings.APPLE_PW = self.passw.GetValue()
        settings.SALES_DIR = self.sales_dir.GetValue()
        
        self.EndModal(wx.ID_OK)

    def OnCancel(self,event):
        """ Cancel Button Clicked """
        self.EndModal(wx.ID_CANCEL)

