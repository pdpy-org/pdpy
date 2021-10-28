# PDDB - Pure Data Data Base Specification

`pddb` is a JSON database that parses the Pure Data source code to get data about
the internal objects. It is useful in the context of the `pdpy` project, with
possible other uses like autocomplete, error check when typing, etc. In the
following text there is a brief description of the JSON data structure.

## Goals

The purpose of this database is to better understand the internal structure of
the `Pure Data` source code, and to enable language checks for the `pdpy` project.
PRs are welcome.

## Loading PDDB with python

You can load `pddb.json` as a json object like this:

```python
import json
with open('pddpy.json') as f:
  data = json.load(f)

print(data)
```

NOTE: the `data` variable will be used in the python examples that follow.

## JSON data structure

This database is an `Array` of `Object`s, meaning that:

1. A single `Array` encloses the entire database.
2. Every element contains exactly one [Entry Object](#entry-object).

## Entry Object

Each **entry** `Object` has two keys named `file` and `classes`. The structure
looks like this:

```json
[
 {
   "file" : '',
   "classes" : []
 }, ...
]
```

### `file`

```python
>>> data[0]['file']
'/path/to/pure-data/extra/pique/pique.c'
```

This key contains exactly one `String` with the path to the Pure Data `.c` file
from which the data of that specific entry was obtained.

In python, you can extract all `file` keys like this:

```python
>>> [entry['file'] for entry in data]
['/path/to/pure-data/extra/pique/pique.c', ... ****]
```

### `classes`

```python
>>> data[0]['classes']
[{'className': 'pique', 'attributes': {'patchable': False, 'newmethod': 'pique_new', 'arguments': {'name': 'pique', 'args': ['A_DEFFLOAT']}, 'methods': ['list', {'name': 'errthresh', 'args': ['A_FLOAT']}], 'description': {'kind': 'data', 'subkind': 'array'}, 'iolets': {'outlets': 1}}}]
```

This key contains an `Array` of [Class Objects](#class-object) that describe the Pure Data classes found in the file path to which `file` points. In this `classes` key you will find most of the data.

## Class Object

Each **class** `Object` has two keys: `className` and `attributes`.

```json
[
 {
   "file": "",
   "classes": [
       {
           "className": "",
           "attributes": {} | []
       }, ...
 }, ...
]
```

### `className`

```python
>>> data[0]['classes'][0]['className']
'pique'
```

This key has exactly one `String` with the name by which this specific class
is refered to internally in the source code.

### `attributes`

```python
>>> data[0]['classes'][0]['attributes']
{'patchable': False, 'newmethod': 'pique_new', 'arguments': {'name': 'pique', 'args': ['A_DEFFLOAT']}, 'methods': ['list', {'name': 'errthresh', 'args': ['A_FLOAT']}], 'description': {'kind': 'data', 'subkind': 'array'}, 'iolets': {'outlets': 1}}
```

This key can hold either one or multiple [Attribute Objects](#attribute-object).
Therefore, it can be either an `Object` or an `Array` of `Object`s and needs
to be parsed accordingly.

## Attribute Object

This `Object` contains variable keys depending on the Pure Data class it describes. The possible keys are:

| Key           | Type                  | Description                                                                                            |
| --------------| :-------------------: | ------------------------------------------------------------------------------------------------------ |
| `patchable`   | `bool`                | Describes if object has inlets or not.                                                                 |
| `newmethod`   | `String`              | The method by which the class is instantiated as a new object.                                         |
| `arguments`   | `Object|String`       | Describes the object's creation arguments. See [Arguments](#arguments).                                |
| `methods`     | `String|Object|Array` | Describes the object's [methods](#methods).                                                            |
| `description` | `Object`              | Describes the object with `kind` and a `subkind`  keys. See [Description Object](#description-object). |
| `iolets`      | `Object`              | Describes the objects `inlets` and `outlets`. See [iolet Object](#iolets-object).                      |
| `signal`      | `bool`                | Describes if object processes audio or not.                                                            |
| `alias`       | `String`              | This contains an alias string that can be used to create the object when patching.                     |
| `help`        | `String`              | This contains the help file identifier when multiple objects are grouped into the same help file.      |

## `arguments`

```python
>>> data[0]['classes'][0]['attributes']['arguments']
{'name': 'pique', 'args': ['A_DEFFLOAT']}
```

This key can either be a `String` or an **argument** `Object` (See [Argument Object](#argument-object))  

### `arguments` Sring

```python
>>> data[3]['classes'][0]['attributes']['arguments']
'loop~'
```

If `arguments` is a `String`, this means that the Pure Data object does not take any arguments except the creation argument. So, the `String` represents the argument needed to create the object when patching.

### `argument` Object

```python
>>> data[23]['classes'][0]['attributes']['arguments']
{'name': 'delay', 'args': ['A_DEFFLOAT', 'A_DEFFLOAT', 'A_DEFSYM']}
```

If `arguments` is an `Object`, then the Pure Data object takes arguments besides its creation argument.

The **argument** `Object` contains a `name` and an `args` keys, for example:

```json
"arguments": {
    "name": "moses",
    "args": [
        "A_DEFFLOAT"
    ]
}
```

#### `argument["name"`]

If the **argument** `Object` is within the `arguments` key, then the `name` key points to the creation argument (e.g., `"moses"` or `"array define"`). 

```python
>>> data[0]['classes'][0]['attributes']['arguments']['name']
'pique'
```

However, it it is within the `methods` key, then the `name` key points to the "message" header. 

For example, in the case of the `netreceive` object, the message header to set the internal port is "listen", and it takes a `list` as argument. This looks like this:

```json
"name": "listen",
"args": [
    "A_GIMME"
]
```

#### `argument["args"]`

The `args` key contains an `Array` of argument types as defined in the Pure Data source code (e.g., `"A_DEFFLOAT"`). The list of possible argument types is:

| Type          | Description                                                                                                              |
| ------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `A_DEFFLOAT`  |  A `float` type argument that can either be present or the Pure Data object falls back to the argument's default value.  |
| `A_GIMME`     |  A `list` of arguments.                                                                                                  |
| `A_DEFSYM`    |  A `symbol` type argument that can either be present or the Pure Data object falls back to the argument's default value. |
| `A_DEFSYMBOL` |  Same as `"A_DEFSYM"`                                                                                                    |
| `A_FLOAT`     |  A `float` type argument that *must* be present.                                                                         |
| `A_SYMBOL`    |  A `symbol` type argument that *must* be present.                                                                        |

## `methods`

This key describes the way to interface with the object via Pure Data "messages". The `methods` key can be either a `String` or an **argument** `Object` or an `Array` combining both.

If there is no `methods` key present, then the object takes no messages.

### `methods` Array

This `Array` can hold a combination of `String` and **argument** `Object`s.
This needs to be taken into account when parsing. Continue reading for each specification.

### `methods` Sring

```python
>>> data[26]['classes'][0]['attributes']['methods']
'list'
```

If `methods` is a `String`, this means that the Pure Data object takes only one message. So, the `String` represents the message that takes exactly one symbol, for example, the "bang" message. The above
example is from the `midiin` object.

### `methods` Object

```python
>>> data[23]['classes'][0]['attributes']['methods']
['bang', 'stop', {'name': 'float', 'args': ['A_FLOAT']}, {'name': 'tempo', 'args': ['A_FLOAT', 'A_SYMBOL']}]
```

This `Object` describes the way to construct the message to interface with the Pure Data object. It is exactly like the arguments object. See [Argument Object](#argument-object).
The above example is from the `delay` object.

## `description` Object

```python
>>> data[26]['classes'][0]['attributes']['description']
{'kind': 'interface', 'subkind': 'midi'}
```

The **description** `Object` contains two keys, `kind` and `subkind`, each holding a `String` that attempts to classify the Pure Data object in the following way:

### `description["kind"]`

These are the different kinds of Pure Data objects that this description performs:

```json
data, signal, interface, parsing, control, operators
```

| Kind | Description |
| ---  |      ---    |
| `signal` | The object processes audio in DSP blocks</td>|
| `interface` | Objects that handle user interface actions |
| `operators` | Control operators |
| `data` | Handle various data structures |
| `parsing` | Parsing functions |
| `control` | Control flow |
| `nonobj` | Non public objects |
| `obsolete` | Objects marked as obsolete |
| `extra` | None of the above `kind` |

### `description["subkind"]`

These are the different sub-kinds of Pure Data objects that this description performs:

```json
array, analysis, midi, generators, block, list, system, time, gui, math, stream, other, text, struct, fourier, filters, canvas, format, network, control_to_sig, flow, delays, comparison, binary, keyboard, route, types
```

### `signal`

| `signal` | Description |
| --- | ---|
| `math` | Performs mathematical functions on the audio block.
| `fourier` | Performs the Fast Fourier Transform on the audio block.
| `filters` | Filters the audio signal block.
| `flow` | Signal object inlets and outlets.
| `delays` | Delays a signal block.
| `route` | Signal routing.
| `generators` | Signal generators.
| `system` | Input/Output to disk or to audio interface.
| `control_to_sig` | Converts control to signal.
| `array` | Interface signals with tables and arrays.
| `block` | Interface to change the DSP block.
| `analysis` | Analyze the signal block.

### `interface`

| `interface` | Description |
| --- | --- |
|`midi` | Handle MIDI input and output |
|`keyboard` | Handle Keyboard events |
|`system` | Handle System events |
|`gui` | Graphical User Interface objects |

### `operators`

| `operators` | Description |
| --- | --- |
| `math` | Mathematical operators |
| `binary` | Binary operators |
| `comparison` | Comparison perators |

### `data`

| `data` | Description |
| --- | --- |
| `array` | Tables and Arrays |
| `struct` | Data Structures |
| `text` | Text objects |
| `canvas` | Subpatches |
| `other` | None of the above |

### `parsing`

| `parsing` | Description |
| --- | --- |
| `list` | Parse list elements |
| `stream` | Parse an incoming stream |
| `forma` | Format parsing |

### `control`

| `control` | Description |
| --- | --- |
| `flow` | Inlets and Outlets|
| `network` | Network objects |
| `math` | Mathematical operations |
| `time` | Delay and time operations |
| `generators` | Control flow Generators |
| `types` | Type casting |

## `iolets` Object

```python
>>> data[35]['classes'][0]['attributes']['iolets']
{'inlets': 2, 'outlets': 1}
```

The **iolets** `Object` contains two keys, `inlets` and `outlets`, each
holding a `Number` that describes how many `inlet` and `outlet` the Pure Data
object box has. The above example is from the `hip~` object.

## Example

This is an example of the `x_misc.c` entry. The only class that is shown is the
`random` class, the rest are omitted:

```json
[
 {
   "file": "/Users/fd/Development/pure-data/src/x_misc.c",
        "classes": [
            {
                "className": "random",
                "attributes": {
                    "patchable": true,
                    "newmethod": "random_new",
                    "arguments": {
                        "name": "random",
                        "args": [
                            "A_DEFFLOAT"
                        ]
                    },
                    "methods": "bang",
                    "description": {
                        "kind": "control",
                        "subkind": "generators"
                    },
                    "iolets": {
                        "inlets": 2,
                        "outlets": 1
                    }
                }
            }, ...
 }, ...
]
```

### Limitations

The `"random"` `className` is located in the `x_misc.c` file. The
Pure Data object is created with the `"random"` symbol and an
optional float (`A_DEFFLOAT`). It has a single method that is
represented by the `"bang"` string, and it is described as a
`control` object of the `generators` subkind. It has `2` inlets and
`1` outlet.

While this is true, it is incomplete. From this description alone,
we are missing information about the functionality of the object.
For example, we cannot know what the object does. Other limitations come from the fact that the `.c` files are not loaded but parsed,
and some object attributes may depend on creation arguments and other
circumstances during instantiation. Accounting for these is still in the todo list.

You are of course welcome to help in any way. Please file an issue or make a PR!

## Credits

Fede Camara Halac (fdch)
Pure Data by Miller Puckette.

