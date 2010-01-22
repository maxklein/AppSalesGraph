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


import sys, wx, settings

# sys.stderr = open("salesgraph_stderr.log", "w")

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

	