# Things to Change

## Fixes

- [ ] rounding error in scientific notation of stored data
- [ ] add new file object classes

## Improvements

- [ ] general purpose make file
- [ ] include author and description attributes from META.pd stuff or externals parsing ?
- [ ] unescape args when encoding to json
- [ ] handle expr arguments differently
- [ ] option to turn class aliases into original names

## Done

- [X] move xml io from Base to another class
- [X] pd method in arrays returns obj instead of array as cls
- [X] pd method in empty messages returns obj instead of msg as cls
- [X] pd method in scalar is not returning the data
- [X] empty object boxes are ommitted
- [X] pd method in struct is not returning the array struct definition
- [X] xml output
- [X] xml input
- [X] doubly escaped comma characters when going from json to pd
- [X] rename classes coherently
- [X] 1st element of text in comments in xml input is lost
- [X] xml: normalize object tags with attribute as real name, ie: `<obj ="*~">`
  