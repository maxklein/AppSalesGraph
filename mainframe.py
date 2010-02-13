# AppSalesGraph: AppStore Sales Graphing
# Copyright (c) 2010 by Max Klein (maximusklein@gmail.com)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

 
import random, sys, locale
import matplotlib.dates as mdates
import wx.lib.masked as masked
import wx.lib.mixins.listctrl    as    listmix

from currency import convert_currency_to_usd
from app_info import AppInfoParser
from popularity_list import PopularityList

from result_event import EVT_RESULT

import datetime, matplotlib, operator, time
import wx, wxmpl
from apps_update import SalesDownloader
from datetime import timedelta
from products_list import ProductsList
from plot_panel import PlotPanel
from sales_list import SalesListCtrl
from reviews_list import ReviewsList
from sales_period import SalesPeriod
from settings_dialog import SettingsDialog
from apps_update import UpdateDownloader

import settings
import wx.animate
import os
import webbrowser
import glob

class MainFrame(wx.Frame):
    
    def ConfigureMenus(self):
        menu = wx.Menu()
        
        ID_IMPORT = wx.NewId()
        menu.Append(ID_IMPORT, "&Import sales files...", "Open")
        menu.AppendSeparator()
        
        ID_PRINT = wx.NewId()
        menu.Append(ID_PRINT, "&Print Graph...", "Print")
        menu.AppendSeparator()
        menu.Append(wx.ID_EXIT, "E&xit", "Terminate the program")
        menu.Enable(ID_PRINT, False)
        # menu.Enable(ID_OPEN, False)
        
        menuBar = wx.MenuBar()
        menuBar.Append(menu, "&File")
       
        menu = wx.Menu()
        ID_UPDATE = wx.NewId()
        ID_AMOUNT = wx.NewId()
        ID_PROFIT = wx.NewId()
        ID_SETTINGS = wx.NewId()
       
        menu.Append(ID_PROFIT, "&Revenue", "Show revenue on graphs", wx.ITEM_RADIO) 
        menu.Append(ID_AMOUNT, "Downloads", "Show downloads on graphs", wx.ITEM_RADIO)
    
        menu.AppendSeparator()
        menu.Append(ID_UPDATE, "&Refresh Sales", "Update From Server")
        menu.AppendSeparator()
        menu.Append(ID_SETTINGS, "&Options...", "Options...")
        menuBar.Append(menu, "&View")
        
        menu = wx.Menu()
        
        ID_HELP = wx.NewId()
        menu.Append(ID_HELP, "&Help Contents", "&Help Contents")
        menu.AppendSeparator()
        
        ID_ABOUT = wx.NewId()
        menu.Append(ID_ABOUT, "&About Salesgraph", "&About Salesgraph")
        menuBar.Append(menu, "&Help")
         
        self.SetMenuBar(menuBar)
        
        
        self.Bind(wx.EVT_MENU, self.OnImport, id=ID_IMPORT)
        self.Bind(wx.EVT_MENU, self.OnSettings, id=ID_SETTINGS)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_MENU, self.OnRefreshSales, id=ID_UPDATE)
        self.Bind(wx.EVT_MENU, self.OnAdd, id=wx.ID_ADD)
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnAmount, id=ID_AMOUNT)
        self.Bind(wx.EVT_MENU, self.OnProfit, id=ID_PROFIT)
        self.Bind(wx.EVT_MENU, self.ShowAboutBox, id=ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.ShowHelp, id=ID_HELP)

    
    
    def ConfigureToolbars(self):
        # img = wx.Image('./images/314246133.jpg') 
        # img.Rescale(48, 48)
        # toolbar = self.CreateToolBar(wx.TB_TEXT | wx.NO_BORDER | wx.TB_HORIZONTAL)
        # toolbar.SetToolBitmapSize((48,48))
        # toolbar.AddLabelTool(1000, "Download Sales", wx.Image('./images/diagram_32.png').ConvertToBitmap())
       # toolbar.AddLabelTool(1001, "Download Reviews", wx.Image('./images/bubble_32.png').ConvertToBitmap())
       # toolbar.AddSeparator()
       # toolbar.AddLabelTool(1001, "Add Event", wx.Image('./images/flag_32.png').ConvertToBitmap())
        toolbar.Realize()
        
        self.Bind(wx.EVT_MENU, self.OnDownloadSalesReports, id=1000)
        self.Bind(wx.EVT_MENU, self.OnServerUpdate, id=1001)
        
        self.status = self.CreateStatusBar()
    
    def ConfigureSizers(self):
        self.uber_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.graphics_sizer = wx.BoxSizer(wx.VERTICAL)
        self.notebook_frame = wx.BoxSizer(wx.VERTICAL)
        
        self.notebook_frame.SetMinSize((640, 480))
        
        
    def ConfigureListCtrls(self):
        self.products_id = wx.NewId()
        self.products = ProductsList(self, self.products_id)
        self.review_list = ReviewsList(self.notebook)
        self.popularity_list = PopularityList(self.notebook)

            
    def ConfigureOtherPanels(self):
        self.notebook = wx.Notebook(self, style=wx.BK_TOP)
        self.notebook_frame.Add(self.notebook, 1, wx.EXPAND|wx.ALL, 15)
        self.notebook_frame.Fit(self)
       
        self.load_label = wx.StaticText(self, label="Loading files...")
        self.load_label.SetBackgroundColour(settings.PRODUCTS_BG_COLOR)
        self.load_label.Raise()
        self.throbber = wx.animate.GIFAnimationCtrl(self, 1, "images/25-0.gif", pos=(10, 10))
        self.throbber.Play()
    
    def ConfigureBottomBar(self):
        
        # Create a bar at the bottom
        self.bottom_box = wx.BoxSizer(wx.HORIZONTAL)
        
        self.refresh_img = wx.Image("images/refresh_button3.png")
        self.refresh_img_hover = wx.Image("images/refresh_button3_hover.png")
        self.refresh_img_press = wx.Image("images/refresh_button3_pressed.png")
        # self.refresh_btn = wx.BitmapButton(self, -1, img.ConvertToBitmap(), style=wx.BU_EXACTFIT, size=(90, 30))
        self.refresh_btn = wx.StaticBitmap(self, -1, self.refresh_img.ConvertToBitmap(), size=(90, 30))
        self.refresh_btn.Bind(wx.EVT_LEFT_DOWN, self.OnRefreshSales)
       
        self.refresh_btn.Raise()
        
        # Split in two
        bottom_box_left = wx.BoxSizer(wx.VERTICAL)
        bottom_box_left_inside = wx.BoxSizer(wx.HORIZONTAL)
        bottom_box_left.Add(bottom_box_left_inside, 1, wx.LEFT|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 10)
    
        bottom_box_right = wx.BoxSizer(wx.VERTICAL)
        bottom_box_right_inside = wx.BoxSizer(wx.HORIZONTAL)
        bottom_box_right.Add(bottom_box_right_inside, 1, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        
        # Add both halves in correct proportion
        self.bottom_box.AddMany(((bottom_box_left, 1, wx.EXPAND), (bottom_box_right, 3, wx.EXPAND)))
        
        # Create date thing
        self.date_range = wx.Slider(self, settings.MAX_RANGE, 7, 1, 
                                    settings.MAX_RANGE, (-1, -1), (250, -1), 
                                    wx.SL_HORIZONTAL|wx.SL_AUTOTICKS)
        self.date_range.SetTickFreq(15)
        
        self.date_entry = masked.NumCtrl(self, value=7, integerWidth=3, allowNegative=False)
        
        bottom_box_right_inside.Add(self.date_range, 0, wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        bottom_box_right_inside.Add(self.date_entry, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 10)
        bottom_box_right_inside.Add(wx.StaticText(self, label="  Days"), 0, wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL, 0)
        
        self.Bind(wx.EVT_SLIDER, self.OnSliderChange)
        self.Bind(masked.EVT_NUM, self.OnDateEntryChange)
        # self.Bind(wx.EVT_BUTTON, self.OnRefreshSales)
        


        # self.refresh_btn = wx.Button(self, -1, "Refresh", )
        # self.refresh_btn.SetMargins(0, 0)
        bottom_box_left_inside.Add(self.refresh_btn, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 0)
        # self.refresh_btn.SetBitmapHover(img_hover.ConvertToBitmap())
        # self.refresh_btn.SetBitmapSelected(img_press.ConvertToBitmap())
        
        self.refresh_btn.SetMinSize((88, 30))
        
        pos = self.refresh_btn.GetRect()
        self.throbber_sales = wx.animate.GIFAnimationCtrl(self, 1, "images/24-0.gif", pos=(pos.x, pos.y))
        self.throbber_sales.Hide()
        
        self.label_throbber_sales = wx.StaticText(self, label="Refreshing...")
        self.label_throbber_sales.SetFont(wx.Font(settings.BOTTOM_STATUS_TEXT_SIZE, wx.SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD, False, u'Verdana'))
        self.label_throbber_sales.Hide()
        
    def ConfigureDatePicker(self):
        
        static_box = wx.StaticBox(self, -1, "Select range")
        self.static_box = wx.StaticBoxSizer(static_box, wx.HORIZONTAL)
        
        now = wx.DateTime().Today()
        self.date_start = wx.DatePickerCtrl(self, size=(120, -1), style=wx.DP_DEFAULT, name="Date range start")
        self.date_start.SetValue(now - wx.DateSpan(days=7))
        self.date_end = wx.DatePickerCtrl(self, size=(120, -1), style=wx.DP_DEFAULT, name="Date range end")
        self.date_end.SetValue(now)

        label_from = wx.BoxSizer(wx.VERTICAL)
        label_from_s = wx.StaticText(self, label="From:")
        label_from.Add(label_from_s, 1, wx.EXPAND|wx.ALL, 3)
        label_from.Fit(self)
        
        label_to = wx.BoxSizer(wx.VERTICAL)
        label_to_s = wx.StaticText(self, label="To:")
        label_to.Add(label_to_s, 1, wx.EXPAND|wx.ALL, 2)
        label_to.Fit(self)
        
        date_range_sizer = wx.GridSizer(2, 2)
        
        date_range_sizer.AddMany((
            (label_from, 1, wx.ALIGN_RIGHT),
            (self.date_start, 2),
            (label_to, 1, wx.ALIGN_RIGHT),
            (self.date_end, 2)))
        
        # self.static_box.AddMany((
        #        (date_range_sizer, 2, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)))
        
        self.Bind(wx.EVT_DATE_CHANGED, self.OnDateChange)
        self.Bind(wx.EVT_DATE_CHANGED, self.OnDateChange)
        
        self.date_end.Hide()
        self.date_start.Hide()
        label_from_s.Hide()
        label_to_s.Hide()
        static_box.Hide()
        
    def ConfigureTopPanel(self):
        # Panel with revenue and all that
        
         # Add the application image
        img_all = wx.Image('images/all_apps_big.png')
        self.app_image = wx.StaticBitmap(self,  bitmap=img_all.ConvertToBitmap())
        
        self.top_bar_area = wx.BoxSizer(wx.HORIZONTAL)
        
        self.app_text_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.product_name_label = wx.StaticText(self, label="All Products")
        self.product_name_label.SetFont(wx.Font(settings.TOP_FONT_SIZE, wx.SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD, False, u'Helvetica'))
        self.product_name_label.SetForegroundColour((65, 81, 87))
        
        self.revenue_label = wx.StaticText(self, label="Last Sales Report: $0")
        self.revenue_label.SetFont(wx.Font(settings.TOP_FONT_MEDIUM_SIZE, wx.SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD, False, u'Arial'))
        self.revenue_label.SetForegroundColour((65, 81, 87))
        
        self.last_income_label = wx.StaticText(self, label="Daily Average (7 Days): $0.0")
        self.last_income_label.SetFont(wx.Font(settings.TOP_FONT_SMALL_SIZE, wx.SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL, False, u'Arial'))
        self.last_income_label.SetForegroundColour((153, 153, 153))
        
        self.selected_range_label = wx.StaticText(self, label="7 day sales: $0.0")
        self.selected_range_label.SetFont(wx.Font(settings.TOP_FONT_SMALL_SIZE, wx.SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL, False, u'Arial'))
        self.selected_range_label.SetForegroundColour((153, 153, 153))
    
        self.top_bar_area.Add(self.app_image, 0, wx.ALL|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 10)
        
        self.app_text_sizer.Add(self.product_name_label, 0, wx.TOP|wx.ALIGN_LEFT|wx.ALIGN_TOP, 10)
        self.app_text_sizer.Add(self.revenue_label, 0, wx.TOP|wx.ALIGN_LEFT, 10)
        self.app_text_sizer.Add(self.selected_range_label, 0, wx.TOP|wx.ALIGN_LEFT, 10)
        self.app_text_sizer.Add(self.last_income_label, 0, wx.TOP|wx.ALIGN_LEFT, 0)
        
        self.top_bar_area.Add(self.app_text_sizer, 0, wx.ALL|wx.ALIGN_LEFT, 5)
        self.top_bar_area.Add(self.static_box, 1, wx.ALL|wx.ALIGN_RIGHT, 15)
        self.top_bar_area.Fit(self)
  
        label_amt = wx.BoxSizer(wx.VERTICAL)
        
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnProductSelected, id=self.products_id)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnProductSelected,id=self.products_id)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.UpdateLowerWidget)

    def ConfigureBottomPanel(self):
        self.sales_panel = PlotPanel(self.notebook)
        sales_list_ctrl = SalesListCtrl(self.notebook)
    
        self.Update()
        self.notebook.AddPage(self.sales_panel, "Sales Graphs")
        self.notebook.AddPage(self.review_list, "Reviews")
        self.notebook.AddPage(sales_list_ctrl, "Sales Details")
        
        # self.review_list.Hide()
    
    def OnCloseWindow(self, event):
        settings.log("SalesGraph starting exit")
        
        from currency import ExchangeRate
        ExchangeRate.save_currencies()
        ExchangeRate.requestShutdown()
        
        settings.save_settings()
        self.sales_period.requestShutdown()
        
        if not self.sales_downloader == None:
            self.sales_downloader.requestShutdown()
        
        if not self.updater == None:
            self.updater.requestShutdown()
            
        self.Destroy()
        
    def __init__(self):
        super(MainFrame, self).__init__(None, -1, "AppSalesGraph")
                        
        self.version = 1.0
        self.sales_downloader = None
        self.updater = None
        
        icon = wx.Icon("images/key.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        
        settings.load_settings()
        
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        
        # Set structures
        EVT_RESULT(self, self.OnResult)
        self.loaded_dates = []
        self.selected_products = []
        self.event_levels = []
        self.delayed = False
        
        # Build up GUI
        self.ConfigureMenus()
        # self.ConfigureToolbars()
        self.ConfigureSizers()
        self.ConfigureBottomBar()
        self.ConfigureDatePicker()
        self.ConfigureOtherPanels()
        self.ConfigureListCtrls()
        self.ConfigureTopPanel()
        self.ConfigureBottomPanel()
        
        
        self.graphics_sizer.AddMany(((self.top_bar_area, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.LEFT, 5), (self.notebook_frame, 4, wx.EXPAND, 5)))
        self.main_sizer.AddMany(((self.products, 1, wx.EXPAND|wx.ALL, 0), (self.graphics_sizer, 3, wx.EXPAND)))
        
        # label_to.Add(wx.StaticText(self, label="To:"), 1, wx.EXPAND|wx.ALL, 2)
        self.uber_sizer.Add(self.main_sizer, 5, wx.EXPAND|wx.ALL, 0)
        
        # wx.ALL is for sides that border applies to
        self.uber_sizer.Add(item=self.bottom_box, proportion=0, 
                            flag=wx.EXPAND|wx.ALL|wx.FIXED_MINSIZE|wx.ALIGN_BOTTOM,
                            border=0)
        
        
        # self.graph_renderer = operator.attrgetter('paid_downloads')
        
        self.SetSizerAndFit(self.uber_sizer)
        self.CentreOnScreen() 
        
        try:
            self.products.Select(0)
            self.OnProductSelected(None)
        except:
            pass
        
        self.Update()
        
        self.sales_period = SalesPeriod(self)
        self.notebook.sales_period = self.sales_period
        self.popularity_list.SetData(self.sales_period)
        
        if not self.sales_panel == None:
            self.sales_panel.sales_period = self.sales_period

        self.LoadSalesFiles()
        # wx.CallLater(500, self.CheckForUpdateFile, None)
        self.OnProfit(None)
    
    def LoadSalesFiles(self):
        self.load_label.SetLabel("Loading sales files...")
        self.load_label.Raise()
        self.load_label.Show()
        self.throbber.Show()
        self.throbber.Raise()
        
        self.SetStatusText("Loading sales files...")
        self.products.DeleteAllItems()
        self.sales_period = SalesPeriod(self)
        self.sales_period.start()
        self.Refresh()
    
    def OnImport(self, event):
        import glob, shutil
        dialog = wx.DirDialog(self, message = "Select the folder", style = 0)
        
        if dialog.ShowModal() == wx.ID_OK:
            dir = dialog.GetPath() + "/*.txt"
            for file in glob.glob(dir):
                shutil.copyfile(file, settings.SalesDir("/" + os.path.basename(file)))
            
            dlg = wx.MessageDialog(self, "All text files have been imported. Please restart the client to see new graphs", "Success!", wx.OK)
            dlg.ShowModal()
            
        print "Import"
        
    def OnSalesFileLoadComplete(self):
        self.products.LoadImages(self.sales_period.product_ids, self.sales_period.product_names)
        self.load_label.Hide()
        self.throbber.Hide()
        self.SetStatusText("")
        
        try:
            self.products.Select(0)
            self.OnProductSelected(None)
        except:
            pass
        
        self.popularity_list.SetData(self.sales_period)
        
        # Debug
        # self.OnReviewAndIconUpdate(None)
    
    def UpdateRefreshStatus(self, str):
        
        if (str.find("SalesFileLoaded") >= 0):
            t = str[len("SalesFileLoaded")+1:]
            self.load_label.SetLabel(t)
            
        if (str == "SalesDownloadCompleteNoFiles"):
            self.label_throbber_sales.Show()
            self.throbber_sales.Hide()
            self.label_throbber_sales.SetLabel("No new sales report available")
            self.refresh_btn.Show()
            self.OnSize(None)
            self.Refresh()
            self.OnReviewAndIconUpdate(None)
            return
        
        if (str.find("RefreshImageAndReviews") >= 0):
            app_id = str[len("RefreshImageAndReviews")+1:]
            app_id = int(app_id)
            self.products.LoadImage(app_id, self.sales_period.product_names[app_id])
            return
        
        if (str.find("SalesDownloadComplete") >= 0):
            
            self.label_throbber_sales.SetLabel("Reading sales file...")

            
            # Download complete, update sales
            self.refresh_btn.Show()
            self.throbber_sales.Hide()
            self.label_throbber_sales.Show()
            self.OnSize(None)
            
            files = self.sales_downloader.filenames
            for file in files:
                self.sales_period.addSalesFile(file)
            
            self.sales_period.refreshSalesData()
            
            self.label_throbber_sales.SetFont(wx.Font(settings.BOTTOM_STATUS_TEXT_SIZE, wx.SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD, False, u'Verdana'))
            
            t = str[len("SalesDownloadComplete")+1:]
            self.label_throbber_sales.SetLabel(t)
            
            if self.products.GetItemCount() <= 1:
                self.products.LoadImages(self.sales_period.product_ids, self.sales_period.product_names)
                
            sound = wx.Sound("glass.wav")
            sound.Play()
            
            self.OnSize(None)
            self.Refresh()
            self.OnReviewAndIconUpdate(None)
            # self.RefreshSales()
            return
        
        if (str.find("SalesDownloadError") >= 0):
            t = str[len("SalesDownloadError")+1:]
            self.label_throbber_sales.SetLabel(t)
            
            self.refresh_btn.Show()
            self.throbber_sales.Hide()
            self.label_throbber_sales.Show()
            self.OnSize(None)
            self.Refresh()
            self.OnReviewAndIconUpdate(None)
            return
            
        self.label_throbber_sales.SetLabel(str)
    
    def ShowAboutBox(self, evt):
         info = wx.AboutDialogInfo()
         info.SetName(settings.APP_NAME)
         info.SetVersion(settings.APP_VERSION)
         info.SetDescription("Analyse your software sales!")
         info.SetCopyright("(C) 2010 Max Klein : maximusklein@gmail.com")
         wx.AboutBox(info);


    def ShowHelp(self, evt):
         # webbrowser.open("web url help")
		 pass

    def OnRefreshSales(self, item):
        
        self.refresh_btn.SetBitmap(self.refresh_img_press.ConvertToBitmap())
        
        if settings.APPLE_ID == "" or settings.APPLE_PW == "":
            msg = "Your %s is not set. Would you like to set it now?" % ("username" if settings.APPLE_ID == "" else "password")
            dlg = wx.MessageDialog(self, msg, "A little problem", wx.YES_NO | wx.ICON_QUESTION)
            result = dlg.ShowModal() == wx.ID_YES
            dlg.Destroy()
            
            if result == True:
                dlg2 = SettingsDialog(self, -1, "Settings", size=(320, 230),style=wx.DEFAULT_DIALOG_STYLE)
                dlg2.CenterOnScreen()
                # dlg2.SetModal(True)
                val = dlg2.ShowModal()
                
                if settings.APPLE_ID == "":
                    dlg = wx.MessageDialog(self, "Your username is still not set. But fine, let's go ahead..", "Did you do it?", wx.OK | wx.ICON_WARNING)
                    dlg.ShowModal()
            else:
                self.refresh_btn.SetBitmap(self.refresh_img.ConvertToBitmap())
                return

        self.label_throbber_sales.SetFont(wx.Font(settings.BOTTOM_STATUS_TEXT_SIZE, wx.SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL, False, u'Verdana'))
        self.refresh_btn.Hide()
        self.label_throbber_sales.Show()
        self.throbber_sales.Show()
        self.throbber_sales.Play()
        
        self.OnSize(None)
        
        days_to_get = []
        for day,val in self.sales_period.unavailable_days.iteritems():
            days_to_get.append(day)
        
        self.UpdateRefreshStatus("Connecting...")
        
        self.sales_downloader = SalesDownloader(self, days_to_get)
        self.sales_downloader.start()
        
        self.refresh_btn.SetBitmap(self.refresh_img.ConvertToBitmap())
        
    def OnResult(self, event):
        str = event.data
        if (str == "SalesInfoRetrieved"):
            self.OnSalesFileLoadComplete()
            # self.OnServerUpdate(None)
            return
                
        if (str == "ReviewDownloadComplete"):
            # self.products.LoadImages(self.sales_period.product_ids, self.sales_period.product_names)
            self.SetStatusText("")
            self.sales_period.reviews = self.updater.reviews
                        
            return
        
        # print str
        self.UpdateRefreshStatus(str)

    def OnSettings(self, evt):
        """ display the settings dialog """          
        dlg = SettingsDialog(self, -1, "Settings", size=(320, 230),
                             style=wx.DEFAULT_DIALOG_STYLE)
        dlg.CenterOnScreen()
        # original_settings = copy.copy(self.settings)
        val = dlg.ShowModal()
        
        #if val == wx.ID_OK:
        #    self.settings.save
        #else: 
        #    self.settings = original_settings
        #    if self.slideshow_timer.IsRunning():
        #        self.slideshow_timer.Start(1000 * self.settings.slideshow_delay)
        #dlg.Destroy() for some reason this causes crahes...     
        
        
    def OnReviewAndIconUpdate(self, event):
        self.updater = UpdateDownloader(self.sales_period.product_ids, self)
        self.updater.start()
        
    def SetStatusText(self, txt):
        pass
    
    def OnAdd(self, event):
        add_dialog = AddEventDialog(self)
        if add_dialog.ShowModal() == wx.ID_OK:
            self.event_levels.append((
                mdates.date2num(self._wxDate2Python(add_dialog.date.GetValue())),
                add_dialog.text.GetValue()))
            self.UpdateLowerWidget()
                            
    def OnSize(self, event):
        if self.GetAutoLayout():
            self.Layout()

        try:
            products_rect = self.products.GetClientRect()
        except:
            return
        
        # print window_size
        graphics_size = self.notebook.GetClientRect()
        
        self.products.SetColumnWidth(1, products_rect.GetWidth() - 30)
        
        if not self.review_list == None:
            self.review_list.SetColumnWidth(0, graphics_size.GetWidth() - 200)
            self.review_list.SetColumnWidth(1, 100)
            self.review_list.SetColumnWidth(2, 70)
        
        if not self.popularity_list == None:
            self.popularity_list.SetColumnWidth(0, 30)
            self.popularity_list.SetColumnWidth(1, graphics_size.GetWidth() - 200)
        
        throbber_rect = self.throbber.GetClientRect()
        left = (products_rect.GetWidth() / 2) - (throbber_rect.GetWidth() / 2)
        top = (products_rect.GetHeight() / 2) - (throbber_rect.GetHeight() / 2)
        self.throbber.Move((left, top))
        
        label_rect = self.load_label.GetClientRect()
        self.load_label.Move(((products_rect.GetWidth() / 2)  - (label_rect.GetWidth() / 2), top - 30))
        self.load_label.Raise()
        
        refresh_rect = self.refresh_btn.GetRect()
        self.throbber_sales.SetPosition((refresh_rect.x, products_rect.GetHeight() + 17))
        
        if self.refresh_btn.IsShown():
            self.label_throbber_sales.SetPosition((refresh_rect.x + 96, products_rect.GetHeight() + settings.BOTTOM_TEXT_TOP_OFFSET))
        else:
            self.label_throbber_sales.SetPosition((refresh_rect.x + 36, products_rect.GetHeight() + settings.BOTTOM_TEXT_TOP_OFFSET))
        
    def OnExit(self, event):
        self.Close(True)

    def OnSliderChange(self, event):
        date_range = self.date_range.GetValue()
        if date_range <= 0:
            return
        
        self.date_entry.SetValue(date_range)
        self.date_start.SetValue(self.date_end.GetValue() - wx.DateSpan(days=date_range))
        self.UpdateLowerWidget()
    
        self.DisplayProductDataOnTopBar(self.selected_products[0])

    def OnDateEntryChange(self, event):
        date_range = self.date_entry.GetValue()
        if date_range <= 0:
            return
        self.date_range.SetValue(date_range)
        self.date_start.SetValue(
            self.date_end.GetValue() - wx.DateSpan(days=date_range))
        self.UpdateLowerWidget()
        
        self.DisplayProductDataOnTopBar(self.selected_products[0])
        
    def OnDateChange(self, event):
        date_range = (
            self.date_end.GetValue() - self.date_start.GetValue()).GetDays()
        if date_range <= 0:
            return
        self.date_entry.SetValue(date_range)
        self.date_range.SetValue(date_range)
        self.UpdateLowerWidget()
        
        self.DisplayProductDataOnTopBar(self.selected_products[0])

    def DisplayProductDataOnTopBar(self, product_id):
        
        date_to_view = self.sales_period.last_sales_day
        limits = (date_to_view, date_to_view)
        
        if product_id == None:
            self.product_name_label.SetLabel("All Products")
        else:
            self.product_name_label.SetLabel(self.sales_period.product_names[product_id])
        
        rev, cnt = self.sales_period.downloadsForProductOnLastReport(product_id, limits)
        if not rev == None: 
            self.revenue_label.SetLabel("Revenue on Last Report: " + rev)
            sales_for_range, sales_val = self.sales_period.revenueForRange(product_id, self.date_entry.GetValue())
            self.selected_range_label.SetLabel(sales_for_range)        
        
            avg_revenue = self.sales_period.averageRevenueForRange(product_id, self.date_entry.GetValue(), sales_val)
            self.last_income_label.SetLabel(avg_revenue)
        
    def OnProductSelected(self, event):
    
        item = self.products.GetFirstSelected()
        if item == wx.NOT_FOUND:
            products = []
            return
        elif item == 0:
            product_id = None
        else:
            product_id = self.products.GetItemData(item)
                
        self.selected_products = [product_id]
        self.UpdateLowerWidget()
        
        # product_ids = self.selected_products
        date_range = self.date_range.GetValue()

        self.DisplayProductDataOnTopBar(product_id)
        
        if not product_id == None:
            if self.sales_period.reviews.has_key(product_id):                      
                self.review_list.setReviews(self.sales_period.reviews[product_id])
            else:
                self.review_list.setReviews([])
            path = settings.DataDir("images/forapps/%i.jpg" % product_id)
            
            if (self.notebook.GetPageCount() == 4):
                self.notebook.SetSelection(0)
                self.notebook.RemovePage(1)
                self.notebook.Refresh()
        else:
            path = ""
            if (self.notebook.GetPageCount() == 3):
                self.notebook.InsertPage(1, self.popularity_list, "Quick Summary")

            
        if os.path.exists(path):
            try:
                img = wx.Image(path)
            except:
                img = wx.Image('images/all_apps_big.png')
        else:
            img = wx.Image('images/all_apps_big.png')
        
        self.app_image.SetBitmap(img.ConvertToBitmap())
        
        self.label_throbber_sales.Hide()

    def OnAmount(self, event):
        PlotPanel.displayCurrency = False
        self._rendererChange('paid_downloads')

    def OnProfit(self, event):
        PlotPanel.displayCurrency = True
        self._rendererChange('total_price')
        
        
    def _rendererChange(self, renderer):
        self.graph_renderer = operator.attrgetter(renderer)
        if self.notebook.GetCurrentPage().has_graphics:
            self.UpdateLowerWidget()

    @staticmethod
    def _wxDate2Python(wxdate):
        ymd = map(int, wxdate.FormatISODate().split('-')) 
        return datetime.date(*ymd)

    def GetDateLimits(self):
        return (
            self._wxDate2Python(self.date_start.GetValue()),
            self._wxDate2Python(self.date_end.GetValue()))

    def UpdateLowerWidget(self, event=None, delay=True):
    
        # A workaround to avoid repainting twice on item change.
        if self.delayed:
            if not delay:
                self.notebook.GetCurrentPage().Update()
                self.delayed = False
        else:
            self.delayed = True
            wx.CallLater(500, self.UpdateLowerWidget, event, delay=False)
    

        

