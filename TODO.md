# Things to Change

## Fixes

- [ ] rebase Array, (Text, and Scalar) on common new Base
- [ ] rounding error in scientific notation of stored data
- [ ] fix pdpy lang compiler

## Improvements

- [ ] handle expr arguments differently: Arguments class?
- [ ] general purpose make file
- [ ] include author and description attributes from META.pd stuff or externals parsing ?
- [ ] option to turn class aliases into original names

## Done

- [X] add new file object classes
- [X] unescape args when encoding to json
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
  