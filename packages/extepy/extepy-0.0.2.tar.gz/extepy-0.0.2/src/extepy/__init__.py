import sys

if sys.version_info[:2] >= (3, 8):
    from importlib.metadata import version, PackageNotFoundError
else:
    from importlib_metadata import version, PackageNotFoundError

from ._collect import groupby, partition  # noqa: F401
from ._fill import fillerr, fillnone, fillwhen  # noqa: F401
from ._fun import pack, repeat, skewer, unpack  # noqa: F401
from ._hash import filehash  # noqa: F401
from ._import import reload  # noqa: F401
from ._op import argchecker, arggetter, attrchecker, itemchecker, constantcreator  # noqa: F401
from ._seq import cycleperm, prioritize, swap  # noqa: F401

try:
    __version__ = version("extepy")
except PackageNotFoundError:
    __version__ = "unknown"
