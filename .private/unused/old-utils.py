
  # result = []
  # starts = []

  # match = re.finditer(regex, line)
  # for m in match:
  #   if m is not None:
  #     starts.append(m.end() - offset)

  # if len(starts):
  #   # first elemnet
  #   result.append(line[0:starts[0]])
  #   # middle elements
  #   for s in range(0, len(starts)-1, offset):
  #     begin = starts[s] + offset
  #     end = starts[s + 1]
  #     result.append(line[begin:end])
  #   # last element
  #   result.append(line[starts[-1] + offset:])
  # else:
  #   result = [line]
  



# escaped=""


# def matchSemicolon(t):
# # def matchSemicolon(t, char=''):
#   # CHECK PD'S m_binbuf.c line 62: binbuf_text
#   # global escaped
#   # escaped += char
#   # print(repr(escaped))
#   # match = t.endswith(" " + escaped + ";\n")

#   # if match:
#     # print("Match", repr(t))
#     # match = matchSemicolon(t, char="\\")
#   # else:
#     # print("Not Matched",len(t), repr(t))
#   match = re.split(re.compile(r"(?<!\\);$"), t)
#   if len(match):
#     match = True
#   else:
#     print(repr(t))
#     print(match)
#     match = False
  
#   return match

    

#   # line = re.escape(t)
#   # match = re.search(re.compile(r";$"), line)
#   # if match:
#   #   prev = match.start() - 1
#   #   if prev > len(line):
#   #     match = True
#   #     if "end" in line:
#   #       print("---->", line)
#   #   else:
#   #     if "\\" in line[prev]:
#   #       match = False
#   #     else:
#   #       match = True
  

#   # regex = re.compile(r"(?<!\\);(?=\n)")
#   # regex = re.compile(r".*?(?<!\\);(?=\r\n)")
#   # regex = re.compile(r";$")
#   # match = re.search(regex, line)
#   # regex = re.compile(r"^#[XNA].*(?<!\\);$", re.MULTILINE)
#   # match = re.search(regex, t)
#   # if ";\n" in t[-2:]:
#   #   match = True
#   #   # if 6 < len(t):
#   #   regex = re.compile(r"(?<=\s\\\\);")
#   #   match = not re.search(regex,t[-6:])
#   #     if match:

#   # else:
#   #   match = False
  
  
  


# def getCharIndex(t, char=",", escaped=True):
#     """ Find index to character (default comma) in list
     
#      Description
#      -----------
#      Specify `char` or of char is `escaped` (default) or not
     
#      Returns
#      ---------
#      int if present, None otherwise
#     """
#     if escaped:
#       regex = r"(?<=\\)" + re.escape(char)
#       offset = 2
#     else:
#       regex = r"(?<!\\)" + re.escape(char)
#       offset = 0
#     match = re.search(regex, t)
#     if match is not None:
#       return match.start() - offset
#     else:
#       return None


# def getUnescapedCharIndex(t, char=","):
#     """ Find index to non-escaped character (default comma) in list
     
#      Returns
#      ---------
#      int if present, None otherwise
#     """
#     return getCharIndex(t,char,escaped=False)

# def sliceAtChar(t, char=";"):
#   """ Slice a string at a defined unescaped character (default ';')
#   Description
#   ----------
#   This is basically a wrapper to `str.split(';')` to avoid escaped chars

#   Returns
#   ----------
#   A `string` containing the sliced first half of the input string
#   """
#   idx = getUnescapedCharIndex(t, char)
#   if idx is not None:
#     return t[:idx]
#   else:
#     return t

# def getOrAddKey(dic, key):

#   def getKey(key=key, value={}):
#     if key not in dic.keys():
#       dic.update({key:value})
#     return dic[key]

#   return getKey


# def updateDict(dic, key, value):
#   """ Updates a list inside a dictionary
  
#   Description
#   ---------
#   If `key` does not exist in dictionary `dict`, the key-value pair is updated

#   Otherwise, the value already present in the `key` becomes a list if it is not already one, and the `value` gets appended to that list.

#   This uses python's list concatenation `[1,2] + [3,4] = [1,2,3,4]`

#   """
#   if key not in dic.keys():
#     dic.update({ key : value})
#   else:
#     prevList = [dic[key]] if not isinstance(dic[key], list) else dic[key]
#     valueList = [value] if not isinstance(value, list) else value
#     dic.update({ key : prevList + valueList })
  
#   return dic[key]


# def updatePrevKey(dic, key, line):
#     try:
#       d = dic()
#       if d[key] is not None:
#         d[-1].update({key:line})
#     except:
#       # d[key] = line
#       dic(key=key,value=line)


# def updatePrevArrayKey(dic, line, key="data", ftype=float, sep=None):
    
#     if sep is not None:
#       line = list(filter(lambda x:x!=sep, line))

#     line = [ftype(i) for i in line]

#     updatePrevKey(dic, key, line)

