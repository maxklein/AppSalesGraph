# AppSalesGraph: AppStore Sales Graphing
# Copyright (c) 2010 by Max Klein (maximusklein@gmail.com)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

from setuptools import setup
 
from distutils.core import setup
import py2exe
import matplotlib
import glob

img = ("images", glob.glob("images/*.*"))
DATA_FILES = matplotlib.get_py2exe_datafiles()
DATA_FILES = DATA_FILES.append(img)


setup(
	data_files=DATA_FILES,
	options={
		'py2exe': {
			'packages' : ['matplotlib', 'pytz'],
			"dll_excludes": [
				"iconv.dll","intl.dll","libatk-1.0-0.dll",
				"libgdk_pixbuf-2.0-0.dll","libgdk-win32-2.0-0.dll",
				"libglib-2.0-0.dll","libgmodule-2.0-0.dll",
				"libgobject-2.0-0.dll","libgthread-2.0-0.dll",
				"libgtk-win32-2.0-0.dll","libpango-1.0-0.dll",
				"libpangowin32-1.0-0.dll"],
				"dist_dir" : 'dist_win',
			}
		
	},
	name = "SalesGraph",
    description = "Software Sales Plotting Tool",
    version = "1.0",
	windows = [
        {"script": "salesgraph.py",
        "icon_resources": [(1, "key.ico")]
        }
    ],
)
