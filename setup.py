from distutils.core import setup
from scripts.version import get_version

version = ".".join(map(lambda x:str(x), get_version()[0]))

setup(name='pdpy',
      version=version,
      py_modules = [
        'pdpy'
      ])