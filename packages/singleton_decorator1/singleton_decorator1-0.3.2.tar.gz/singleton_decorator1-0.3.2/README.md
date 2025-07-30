###Singleton Decorator Library

A decorator from wiki.python.org Python Decorators Library, namely
https://wiki.python.org/moin/PythonDecoratorLibrary#Singleton

This has some fixes, plus a threadsafe version

from singleton_decorator1 import singleton

or

from singleton_decorator1 import threadsafe_singleton as singleton

The library can be built with poetry >= 2.0:
[Recommended]
if needed, install pyenv
pyenv install 3.10
pyenv local 3.10

[required]
(pip show poetry | grep -q "Version: 2") || pip install --ignore installed poetry==2

poetry env use $(pyenv which python) or
poetry env use $(which python)

poetry install

poetry build


