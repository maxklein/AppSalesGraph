# AppSalesGraph: AppStore Sales Graphing
# Copyright (c) 2010 by Max Klein (maximusklein@gmail.com)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
 
import locale
import matplotlib
import pickle
from pyDes import *
import sys, os, wx
from datetime import datetime
from datetime import date
from currency import ExchangeRate

locale.setlocale(locale.LC_ALL, '')

try:
    date_format = locale.nl_langinfo(locale.D_FMT)
except:
    date_format = '%m/%d/%y'
    
matplotlib.rcParams['font.sans-serif'] = ['Arial',
    'Helvetica', 'Bitstream Vera Sans', 'DejaVu Sans', 'Lucida Grande',
    'Verdana', 'Geneva', 'Lucid', 'Arial', 'Avant Garde', 'sans-serif']

matplotlib.rcParams['font.size'] = 9
matplotlib.rcParams['font.family'] = 'sans-serif'
CRYPT2 = "PubSubAgent." + str(894378)

def display_error(str, title="AppSalesGraph Error!", yes_no=False):
    import wx
    if yes_no == True:
        dlg = wx.MessageDialog(None, str, title, wx.YES_NO | wx.ICON_ERROR)
    else:
        dlg = wx.MessageDialog(None, str, title, wx.OK | wx.ICON_ERROR)
    result = dlg.ShowModal() == wx.ID_YES
    return result

def SalesDir(str = None):
    global SALES_DIR
    if not str == None:
        return SALES_DIR + "/" + str
    
    return SALES_DIR

def DataDir(str = None):
    if not str == None:
        return  wx.StandardPaths.Get().GetUserDataDir() + "/" + str
    
    return wx.StandardPaths.Get().GetUserDataDir()

def do_one_time_debug_init():
    
    # import currency
    # currency.download_all_currencies()
    
    if not os.path.exists(DataDir()):
        os.makedirs(DataDir())
    
    try:
        sales = SalesDir("sales_data")
        os.makedirs(sales)
    except:
        pass
    
    try:
        os.makedirs(DataDir("sales_data/xml/"))
    except:
        pass

    try:
        os.makedirs(SalesDir("double/"))
    except:
        pass
    
    try:
        os.makedirs(DataDir("images/forapps/"))
    except:
        pass

    
    if not os.path.exists(DataDir("currencies.key")):
        import shutil
        shutil.copyfile("currencies.key", DataDir("currencies.key"))
    
    log("DataDir: " + DataDir())
    
    # Create date file
    loc = wx.StandardPaths.Get().GetUserConfigDir()
    if not loc[len(loc)-1] == "/":
        loc = loc + "/"

    # Load currentcy file
    ExchangeRate.get("USD")
    
def format_currency(val):
    return "$" + str(round(val, 2))

def start_log():
    # os.remove("log.txt")
    try:
        file = open(DataDir("log.txt"), "w") # read mode
        file.write("AppSalesGraph 1.1 -- " + datetime.today().__str__() + "\r\n")
        file.write("OS: " + sys.platform + "\r\n\r\n")
        file.close()
    except:
        pass
    
    # Disable the shutdown messagebox
    # sys.stdout = open("salesgraph_stdout.log", "w")
    # sys.stderr = open("salesgraph_stderr.log", "w")
    
def log(str):
    print str
    
    try:
        file = open(DataDir("log.txt"), "a") # read mode
        file.write(str + "\r\n")
        file.close()
    except:
        pass

def gen_phrase():
    PASSPHRASE = ""
    PASSPHRASE = PASSPHRASE + chr(32)
    for i in range(65, 128):
        if i%10 == 0:
            PASSPHRASE = PASSPHRASE + chr(65 + i%30)
    PASSPHRASE = PASSPHRASE + chr(40)
    return PASSPHRASE
        
def save_settings():
    
    global APPLE_ID
    global APPLE_PW
    global SALES_DIR
    
    k = des(gen_phrase())
    settings_info = {"_" : k.encrypt(APPLE_ID.encode('ascii'), " "),
                     "-" : k.encrypt(APPLE_PW.encode('ascii'), " "),
                     "sales_dir" : SALES_DIR}
    
    file_name = DataDir("settings.dat")
    
    try:
        file = open(file_name, "w") # read mode
        pickle.dump(settings_info, file)
        file.close()
    except:
        print("CANNOT SAVE SETTINGS")

def load_settings():
    
    global SALES_DIR
    global APPLE_ID
    global APPLE_PW
    
    SALES_DIR = DataDir("sales_data")
    file_name = DataDir("settings.dat")
    
    try:
        file = open(file_name, "r") # read mode
    except:
        return
            
    try:
        settings_info = pickle.load(file)
    except:
        file.close()
        return
    

    
    k = des(gen_phrase())
    APPLE_ID = k.decrypt(settings_info["_"], " ")
    APPLE_PW = k.decrypt(settings_info["-"], " ")
    if settings_info.has_key('sales_dir'):
        SALES_DIR = settings_info['sales_dir']
        if (SALES_DIR == None or SALES_DIR == ""):
            SALES_DIR = DataDir("sales_data")
        
    file.close()

CRYPT1 = "system"
APP_NAME = "AppSalesGraph"
APP_VERSION = "0.5"
DAYS_TO_SHOW = 90
IMAGE_SIDE = 32
MAX_TICKS = 15
MAX_RANGE = 365
BIG_IMAGES = False

SALES_DIR = ""

PRODUCTS_BG_COLOR = (235,240,248)
APPLE_ID = ''
APPLE_PW = ''
DOWNLOAD_REVIEWS = True
DOWNLOAD_SALES = True
MOVE_DOUBLE_FILES = True
DAYS_TO_CHECK = 7
DAYS_LEFT = -1
if sys.platform == "win32":
    IS_WINDOWS = True
    PRODUCT_FONT_SIZE = 11
    PRODUCTS_FONT = "Candara"
    TOP_FONT_SIZE = 11
    TOP_FONT_MEDIUM_SIZE = 11
    TOP_FONT_SMALL_SIZE = 9
    BOTTOM_STATUS_TEXT_SIZE = 8
    BOTTOM_TEXT_TOP_OFFSET = 24
else:
    IS_WINDOWS = False
    PRODUCT_FONT_SIZE = 13
    PRODUCTS_FONT = "Helvetica"
    TOP_FONT_SIZE = 20
    TOP_FONT_MEDIUM_SIZE = 14
    TOP_FONT_SMALL_SIZE = 12
    BOTTOM_STATUS_TEXT_SIZE = 10
    BOTTOM_TEXT_TOP_OFFSET = 20
    