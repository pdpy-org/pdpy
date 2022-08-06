"""
	pd2json

	This package turns .pd files into json objects
	
	variables:
		pdtype

	functions:

	helpers:

		mapper(arr)
		map_text(arr)

	main:

		load_pdfile(file)
		pd2json(patchlist)
		write(objectlist,target)

	questions to fdch.github.io


"""
from ast import literal_eval 	# for evaluating string for int/float
from json import dump 			# for writing json to file

pdtype={

	"#N" : [ 
		"canvas", 
		"struct" 
	],
	"#X" : [ 
		"restore", 
		"declare", 
		"coords", 
		"connect", 
		"obj",
		"array",
		"floatatom", 
		"symbolatom", 
		"msg", 
		"text",
	],	
	"#A" : [ 
		"0",
		"set" 
	]
	
}

def mapper(arr):
	"""
	@brief      Return array with correct types
	
	@param      arr   The imput array 
	
	@return     Array with correct types
	"""
	if not isinstance(arr,str):
		d=[]
		a=[]
		for i in arr:
			d.append(i.replace(";",""))
		for x in list(filter(None,d)):
			try:
				a.append(literal_eval(x))
			except:
				a.append(x)
		return a
	else:
		d=arr.replace(";","")
		return literal_eval(d)

def map_text(arr):
	"""
	@brief      Split puredata [text] lines by semicolons into array
	
	@param      arr   The input array
	
	@return     An array with one [text] line per val
	"""
	a=[]
	for x in (" ".join(arr)).split(";"):
		a.append(x.strip())
	return mapper(a)

def map_scalar(arr):
	dstruct=[]
	d={}
	for x in range(0,len(arr)-1,2):
		if (arr[x] == "float") or (arr[x] == "symbol") or (arr[x] == "array"):
			d={
				"type":arr[x],
				"name":arr[x+1],
			}
			if arr[x] == "array":
				d.update({
					"template":arr[x+2]
				})
			dstruct.append(d)
	return dstruct

def load_pdfile(file):
	"""
	@brief      Loads a Pure Data (*.pd) file into a python list
	
	@param      file  The file
	
	@return     The pd file as a list
	"""
	patch=[]
	with open(file, "r") as p:
		for v in p:

			# trim newlines and backslashes:

			# l=v.replace(";","").replace("\n","").replace("\\","").split(" ")
			l=v.replace("\n","").replace("\\","").split(" ")
			l=list(filter(None, l))
			# l=v.replace(";","[SC]").replace("\n","[NL]").replace("\\","[BS]").split(" ")

			#	make sure lines extend pdtypes if they are not a pdtype

			if l[0] in pdtype.keys():
				patch.append(l)
			else:
				patch[len(patch)-1].extend(l)
	return patch

def pd2json(patchlist):
	"""
	@brief      Parse the input for Pure Data elements
	
	@param      patchlist  The patchlist
	
	@return     The json object with the patch list.
	"""

	objectlist={}

	objectlist["graph"]={}
	objectlist["graph"]["nodes"]=[]
	c=0
	depth=-1

	for i,v in enumerate(patchlist):
		
		data={
		
			"pdtype":v[1]
		
		}

		if v[1] == "canvas": #canvas
			depth+=1
			data.update({
				"x":int(v[2]),
				"y":int(v[3]),
				"w":int(v[4]),
				"h":int(v[5])
				})

			if len(v) == 7: # the root canvas

				c=-1 # reset object count to -1
			
				data.update({
					"fsize":mapper(v[6])
					})
			
			else: # subcanvases
				
				c+=1
				

				data.update({
					"name":v[6],
					"vis":mapper(v[7])
					})

		elif v[1] == "struct": #struct
			data.update({
				"s_name": v[2],
				"s_data": map_scalar(v[3:])
				})

		elif v[1] == "restore": #restore
			
			depth-=1

			data.update({
				"x":int(v[2]),
				"y":int(v[3]),
				"args":" ".join(v[4:])
				})

		elif (v[1] == "declare"):
			data.update({
				"args":v[2:]
				}) 
		
		elif (v[1] == "coords"):
			data.update({
				"args":mapper(v[2:])
				}) 

		elif (v[1] == "connect"):
			data.update({
				"args":mapper(v[2:])
				})

		elif v[1] == "0": # a kept array
			data["pdtype"]="k_array"
			data.update({
				"a_data":mapper(v[2:])
				})

		elif v[1] == "set": # an kept text
			data["pdtype"]="k_text"
			data.update({
				"t_data":map_text(v[2:])
				})

		elif v[1] == "scalar":
			data.update({
				"s_name":v[2],
				"s_data":mapper(v[3:])
				})
		
		else: # these objects increment object count
			c+=1
			if v[1] == "array":
				data.update({
				"name":v[2],
				"size":mapper(v[3]),
				"args":mapper(v[4:])
				})
			else:
				data.update({
					"x":mapper(v[2]),
					"y":mapper(v[3])
					})

				if v[1] == "obj":
					data.update({
						"name":v[4],
						"args":mapper(v[5:])
						})
				elif (v[1] == "floatatom") or ( v[1] == "symbolatom"):
					data.update({
						"size"   :mapper(v[4]),
						"min"    :mapper(v[5]),
						"max"    :mapper(v[6]),
						"lpos"   :mapper(v[7]),
						"label"  :v[8],
						"send"   :v[9],
						"receive":v[10]
						})
				elif v[1] == "text":
					data.update({
						"args":map_text(v[4:])
						})
				elif v[1] == "msg":
					data.update({
						"args":v[4:] # dont replace ; in messages
						})
				else:
					print(f"what is this?: {v}")
		if depth >= 1:
			cnt=c
		else:
			cnt=-1

		data.update({
			"depth":depth,
			"object_count":cnt,
		})


		objectlist["graph"]["nodes"].append({"id":i,"data":data})

	return objectlist

def write(objectlist,target):
	"""
	@brief      Write the json object to target file
	
	@param      objectlist  The object list
	@param      target     The target file
	
	@return     void
	"""
	with open(target, "w") as f:
		dump(objectlist,f,indent=2)

def find_by_type(objectlist,pdtype):
	"""
	@brief      Gets the node by type.
	
	@param      objectlist  The objectlist
	@param      pdtype      The pd type
	
	@return     An array with all nodes containing the queried type
	"""
	v=[]
	for i in objectlist['graph']['nodes']:
		if i['data']['pdtype'] == pdtype:
			v.append(i)
	return v

if "__main__" in __name__:
  
  import sys
  from ntpath import basename

  if len(sys.argv) == 2:
    if isinstance((sys.argv[1]), str):
      source = sys.argv[1]
      target = basename(source) + ".json"
  else:
    print("Must provide the patch file as argument 1")
    quit()

  # print pd2json.pdtype

  patchlist = load_pdfile(source)

  objectlist = pd2json(patchlist)

  write(objectlist, target)

