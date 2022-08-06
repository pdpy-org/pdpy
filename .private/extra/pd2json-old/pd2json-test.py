#
#	GET DATA FROM PURE DATA FILES INTO JSON FILES
#
#	Run: 
#	
#	$ python pd2json-test.py filename
#
#
#
#
#
#
from sys import argv			# for argument parsing
from ntpath import basename		# for path stripping

import pd2json 					# outputs a pd file as json object

if len(argv) == 2:
	if isinstance((argv[1]), str):
		source=argv[1]
		target=basename(source)+".json"
else:
	print "Must provide the patch file as argument 1"
	quit()

# print pd2json.pdtype

patchlist=pd2json.load_pdfile(source)

objectlist=pd2json.pd2json(patchlist)

pd2json.write(objectlist,target)