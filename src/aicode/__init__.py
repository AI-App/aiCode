"""`aicode` package."""


from collections.abc import Sequence
from importlib.metadata import version
from typing import LiteralString


__all__: Sequence[LiteralString] = ('__version__',)


__version__: str = version(distribution_name='aiCode')
