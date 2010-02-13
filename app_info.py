import xml.sax

# AppSalesGraph: AppStore Sales Graphing
# Copyright (c) 2010 by Max Klein (maximusklein@gmail.com)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
 

class AppInfoParser(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.mapping = {}
        self.image_url = ""
        self.inReviewName = False
        self.inTextView = False
        self.textViewData = ""
        self.foundReview = False
        self.reviewHeaderRead = False
        self.current_review= {}
        self.reviews = []
        
    def startElement(self, name, attributes):
        self.buffer = ""
        
        if name == "TextView":
            self.inTextView = True
            self.textViewData = ""
            
        if name == "PictureView":
           alt = attributes.getValue("alt")
           if alt.find("artwork") > 0:
               self.image_url = attributes.getValue("url")

        if name == "GotoURL":
            url = attributes.getValue("url")
            if url.find("userProfileId") > 0:
                self.inReviewName = True
        
    def characters(self, data):
        if self.inReviewName == True:
            self.buffer += data
        
        if self.inTextView == True:
            self.textViewData = self.textViewData + data
            
    def endElement(self, name):

        if name == "TextView":
            if self.reviewHeaderRead == True:
                self.reviewHeaderRead = False
                
                review_body = self.textViewData
                review_body = review_body.encode("utf-8", 'ignore')
                

                # print review_body
                
                self.current_review["ReviewBody"] = review_body
                
                new_review = {}
                new_review["ReviewBody"] = review_body
                new_review["ReviewHeader"] = self.current_review["ReviewHeader"]
                self.reviews.append(new_review)
                
            if self.textViewData.find("by") > 0 and self.inReviewName == True:
                review_header = self.textViewData.strip(" \n\r\t")
                # review_header = review_header.replace("\nby", "by ")
                review_header = review_header.replace("\n", " ")
                # review_header = review_header.replace("\t", "")
                # review_header = review_header.replace("\r", "")
                review_header = review_header.replace("  ", "")
                # review_header = review_header.replace("  ", "")
                review_header = review_header.replace("-", " - ")
                review_header = review_header.replace("-  ", "- ")
                review_header = review_header.replace("  -", " -")
                review_header = review_header.encode("utf-8")
                
                self.current_review["ReviewHeader"] = review_header
                # print review_header
                
                self.reviewHeaderRead = True
            
            self.inReviewName = False
            self.foundReview = False
            self.inTextView = False
            self.textViewData = ""
             
             
		
