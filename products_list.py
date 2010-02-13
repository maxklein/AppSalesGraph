# AppSalesGraph: AppStore Sales Graphing
# Copyright (c) 2010 by Max Klein (maximusklein@gmail.com)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

 
import wx
import wx.lib.mixins.listctrl as listmix
import os, sys
import settings


class ProductsList(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, id):
        super(ProductsList, self).__init__(
            parent, id=id,
            style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.LC_SINGLE_SEL|wx.NO_BORDER)
        
        # |wx.NO_BORDER
        
        self.InsertColumn(0, "Image", wx.LIST_FORMAT_RIGHT)
        self.InsertColumn(1, "Item")

        self.SetColumnWidth(0, 5)
        self.SetColumnWidth(1, 170)
        self.SetBackgroundColour(settings.PRODUCTS_BG_COLOR)
        
        self.img_all = wx.Image("images/archive.png")
        self.img_all.Rescale(settings.IMAGE_SIDE, settings.IMAGE_SIDE)

        first_added = False

        img = wx.Image("images/iCube_32.png")
        img.Rescale(settings.IMAGE_SIDE, settings.IMAGE_SIDE)
        
        self.null_bmp = img.ConvertToBitmap() # wx.NullBitmap
        
        self.il = wx.ImageList(settings.IMAGE_SIDE, settings.IMAGE_SIDE)
        image_index = self.il.Add(self.img_all.ConvertToBitmap())
        self.SetImageList(
            self.il,
            wx.IMAGE_LIST_NORMAL if settings.BIG_IMAGES else wx.IMAGE_LIST_SMALL)
        

    def LoadImage(self, product_id, product_name):
        path = settings.DataDir("images/forapps/%i.jpg" % product_id)

        if os.path.exists(path):
            try:
                img = wx.Image(path)
                img.Rescale(settings.IMAGE_SIDE, settings.IMAGE_SIDE, quality=wx.IMAGE_QUALITY_HIGH)
                bmp = img.ConvertToBitmap()
            except:
                os.remove(path)
                bmp = self.null_bmp
        else:
            bmp = self.null_bmp
                
        image_index = -1
        if product_id == -1:
            image_index = self.il.Add(self.img_all.ConvertToBitmap())
        else:
            image_index = self.il.Add(bmp)
        
        index = self.FindItemData(-1, product_id)
        if index == -1:
            index = self.InsertStringItem(sys.maxint, "", -1)
            self.SetItemColumnImage(index, 1, image_index)
        else:
            self.SetItemColumnImage(index, 1, image_index)
            # self.SetItemImage(index, image_index)
            
        self.SetStringItem(index, 1, product_name)

        font = self.GetItemFont(index)
        font.SetPointSize(settings.PRODUCT_FONT_SIZE)
        font.SetFaceName(settings.PRODUCTS_FONT)
        self.SetItemFont(index, font)
        self.SetItemData(index, product_id)
        self.RefreshItem(index)
            
    def LoadImages(self, product_ids, product_names):
        all_ids = [-1] + product_ids[:]
        all_products = {-1: "All Products"}
        all_products.update(product_names)
        for id in all_ids:
            self.LoadImage(id, all_products[id])
