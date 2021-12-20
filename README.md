# pdpy

A python package to interact with Pure Data (Pd) from Python (py).

Translate Pure Data files from the `.pd` format to other formats such as JSON or XML.

## Example

Translate the Pure Data 'testtone.pd' patch into a JSON-formatted string in 'testtone.json':

``` python
import pdpy
# initialize the translator object with an input file and a target format
translator = pdpy.Translator('./tests/testtone.pd', to='json')
# run the translator
translator()
```

The result is something like this:

``` json
{
    "patchname": "testtone.pd",
    "encoding": "utf-8",
    "__pdpy__": "PdPy",
    "root": { ... 
}
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
