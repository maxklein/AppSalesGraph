# AppSalesGraph: AppStore Sales Graphing
# Copyright (c) 2010 by Max Klein (maximusklein@gmail.com)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
 

import sys, wx, settings


class SalesGraphApp(wx.App):
	def OnInit(self):
	
		self.SetAppName(settings.APP_NAME)
			
		settings.do_one_time_debug_init()
		settings.start_log()
		
		from mainframe import MainFrame
		self.frame = MainFrame()
		self.frame.SetBackgroundColour( wx.Colour( 255, 255, 255 ) );
		self.frame.Show(True)
		self.SetTopWindow(self.frame)
		return True

	def OnExit(self):
		settings.log("App Exit")
        
app = SalesGraphApp(0)
app.MainLoop()

	