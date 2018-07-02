# A shell script that can optionally compute what percentage of the 
# application code is test covered (output in report.txt in the current directory).
# To use first install Ned Batchelder's coverage.py: http://nedbatchelder.com/code/coverage/
coverage -x manage.py test dj
coverage -r -m > report.txt

