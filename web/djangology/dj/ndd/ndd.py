#! /usr/bin/env python
# Main near-duplicate detection "runner"
#
# Written by Parker Moore (pjm336)
# http://www.parkermoore.de

import operator, copy
from detector import Detector
import psycopg2

if __name__ == "__main__":
    # run the program
    detector = Detector('./test')
    print "Checking for duplicates using NDD..."
    duplicates = detector.check_for_duplicates()
    if duplicates:
        print "Duplicates found (Jaccard coefficient > 0.5):"
        print duplicates
    filenames_of_first_one_hundred = []

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
    print "\nRows: \n"
    for row in rows:
	filenames_of_first_one_hundred.append(row[0])
    cur.close()


    print "Printing three nearest neighbors of the first 10 files..."
    print(filenames_of_first_one_hundred)
    filenames_of_first_ten = [20]
    for index1, j in enumerate(filenames_of_first_ten):
	print("1,j",index1,j)
        jaccard_coefficients = [-1] * len(filenames_of_first_one_hundred)
        for index2, d in enumerate(filenames_of_first_one_hundred):
            if d != j:
	    	print("2,d",index2,d)
                jaccard_coefficients[index2] = detector.index.get_jaccard(j, d)
        three_nearest = []
        nearest_count = -1
        jcos = copy.deepcopy(jaccard_coefficients)
	print(jcos)
        while len(three_nearest) < 3:
            index,coefficient = max(enumerate(jcos), key=operator.itemgetter(1))
            del jcos[index]
            # put the index back where it was in the original jaccard_coefficients
            if nearest_count == 0 and index >= three_nearest[0][0]:
                index += 1
            if nearest_count == 1:
                if index >= three_nearest[0][0]:
                    index += 1
                if index >= three_nearest[1][0]:
                    index += 1
            three_nearest.append((index,coefficient))
            nearest_count += 1
	print(three_nearest)
        print "Three nearest neighbors to %s:" % ("file%02d.txt" % j)
        for near in sorted(three_nearest, key=operator.itemgetter(1), reverse=True):
            print "\t%s with Jaccard coefficient of %0.3f" % ("file%02d.txt" % filenames_of_first_one_hundred[near[0]], near[1])
