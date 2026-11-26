"""NetBox Software Discovery plugin.

NetBox loads a plugin by importing this package and reading its ``config`` attribute.
"""

from .apps import config

__all__ = ["config"]
