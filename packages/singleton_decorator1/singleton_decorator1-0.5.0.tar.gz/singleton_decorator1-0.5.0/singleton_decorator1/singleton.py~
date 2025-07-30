"""
Defines a decorator function, which can manage multiple classes as singletons
Copyright (C) 2011  "Editor: 82 of wiki.python.org"

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import functools

# from decorator import decorator
# @decorator
# actually dont anotate with @decorator: that makes great FUNCTION decorators


def singleton(cls):
    """
    Use class as singleton, by modifications to __new__ and __init__
    Modifying __del__ is not required, since cls.__it__ ensures we will
    always have a pointer to the singleton after it is created, so
    it will never be garbage collected.
    """

    # preserve original initializations
    cls.__new_original__ = cls.__new__
    cls.__init_original__ = cls.__init__
    cls.__it__ = None

    # create a new "new" which usually returns
    # __it__, the single instance
    @functools.wraps(cls.__new__)
    def singleton_new(cls, *args, **kw):
        it = cls.__dict__.get("__it__")
        if (len(args) + len(kw)) > 0:
            print(
                """
Singleton Warning: singletons are intended to be single instance, and thus
not customizable. Arguments are not recommended, and are ignored after the
first instantiation. Consider using pypi "simple-singleton", which is like
a singleton, but expects variations.
            """,
                file=sys.stderr,
            )
        if it is not None:
            return it
        cls.__it__ = it = cls.__new_original__(cls, *args, **kw)
        cls.__init_original__(it, *args, **kw)
        return it

    # and a new init which does nothing (more)
    def singleton_init(self):
        return

    # and copy operations that don't
    def singleton_copy(self):
        return cls.__it__

    def singleton_deepcopy(self, memo):
        return cls.__it__

    # Change new to the new one
    cls.__new__ = singleton_new
    cls.__init__ = singleton_init
    cls.__copy__ = singleton_copy
    cls.__deepcopy__ = singleton_deepcopy

    return cls
