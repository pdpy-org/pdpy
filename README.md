# pdpy

A python package to interact with Pure Data (Pd) from Python (py).

Translate Pure Data files from the `.pd` format to other formats such as JSON or XML.

## Example

Translate the Pure Data 'hello-world.pd' patch into a JSON-formatted string in 'hello-world.json':

``` python
import pdpy
# initialize the translator object with an input file and a target format
translator = pdpy.Translator('./tests/hello-world.pd', to='json')
# run the translator
translator()
```

The result is something like this:

``` json
{
    "patchname": "testtone.pd",
    "encoding": "utf-8",
    "__pdpy__": "PdPy",
    "root": {
        "__pdpy__": "Canvas",
        "isroot": true,
        "name": "testtone.pd",
        "vis": 1,
        "screen": {
            "__pdpy__": "Point",
            "x": 273,
            "y": 107
        },
        "dimension": {
            "__pdpy__": "Size",
            "width": 607,
            "height": 373
        },
        "font": 12,
        "nodes": [
            {
                "__pdpy__": "PdNativeGui",
                "id": 0,
                "position": {
                    "__pdpy__": "Point",
                    "x": 86,
                    "y": 273
                },
                "className": "floatatom",
                "digit_width": "3",
                "limits": {
                    "__pdpy__": "Bounds",
                    "lower": 0.0,
                    "upper": 0.0
                },
                "flag": "0",
                "label": "-",
                "comm": {
                    "__pdpy__": "Comm",
                    "send": "-",
                    "receive": "-"
                }
            },
            {
                "__pdpy__": "PdObject",
                "id": 1,
                "position": {
                    "__pdpy__": "Point",
                    "x": 27,
                    "y": 221
                },
                "className": "notein"
            }, ...
```

## References

Pure Data to XML:
<https://lists.puredata.info/pipermail/pd-dev/2004-12/003316.html>

Pure Data to JSON:
<https://lists.puredata.info/pipermail/pd-dev/2012-06/018434.html>

new file format :
<https://lists.puredata.info/pipermail/pd-dev/2007-09/009483.html>

PURE DATA FILE FORMAT
<http://puredata.info/docs/developer/PdFileFormat>

sebpiq's web pd project:
<https://github.com/sebpiq/WebPd_pd-parser>
<https://github.com/sebpiq/pd-fileutils>
