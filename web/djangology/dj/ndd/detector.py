# -*- coding: utf-8 -*-

# Detector class
#
# Written by Parker Moore (pjm336)
# http://www.parkermoore.de

import os
from ndindex import NearDuplicatesIndex
import psycopg2

class Detector:
    def __init__(self, test_docs_dir="./test"):
        self.test_docs_dir = test_docs_dir
        self.files = []

        self.index = NearDuplicatesIndex()

        # Calculate near-duplicates index




	# Try to connect

	try:
	    conn=psycopg2.connect("dbname='djangology' user='ubuntu' password=''")
	except:
	    print "I am unable to connect to the database."

	cur = conn.cursor()
	try:
	    cur.execute("""SELECT * from dj_document""")
	except:
	    print "I can't SELECT from dj_document"

	rows = cur.fetchall()
	#print "\nRows: \n"
	for row in rows:
	    #print "   ", row[1]
            self.index.append(row[1], row[0])
	    self.files.append(row[0])
	cur.close()

        #for file in self.files:
         #   filename = self.filename(file)
          #  with open(filename) as f:
           #     doc = f.read().strip().strip(",.!|&-_()[]<>{}/\"'").strip().split(" ")
                #self.index.append(doc, filename)

    # Public: returns the full relative path from the base dir of the project
    #         to the filename input
    #
    # filename - the filename relative to the test directory
    #
    # Returns full filename (including test directory)
    def filename(self, filename):
        return "%s/%s" % (self.test_docs_dir, filename)

    # Public: checks for near-duplicates in the set of files based on jaccard
    #         coefficient threshold of 0.5
    #
    # Returns a string containing formatted names and coefficients of 
    #   documents whose jaccard coefficient is greater than 0.5
    def check_for_duplicates(self):
        matches = []
        for indx1, f1 in enumerate(self.files):
            for indx2, f2 in enumerate(self.files[indx1+1:]):
                jaccard = self.index.get_jaccard(f1, f2)
                if jaccard > 0.5:
                    matches.append("%s and %s are near-duplicates, with Jaccard value of %0.3f." % (f1, f2, jaccard))
        return "\n".join(matches)
