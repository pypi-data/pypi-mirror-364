"""
teradataml-plus
============================
Python Package that extends the functionality of the popular [teradataml](https://pypi.org/project/teradataml/) package through [monkey-patching](https://en.wikipedia.org/wiki/Monkey_patch).
This is to use field-developed assets more naturally with the existing interface.
"""

__author__ = """Martin Hillebrand"""
__email__ = 'martin.hillebrand@teradata.com'
__version__ = '0.1.0'



# Public monkey-patched API provided by tdmlplus
__all__ = [
    "teradataml.DataFrame.corr",
    "teradataml.random.randn",
    "teradataml.dba.get_amps_count",
]


import teradataml as tdml
try:
    tdml.display.enable_ui = False
except:
    pass


# --- patch: DataFrame.corr ---
from .patch.dataframe import corr
if not hasattr(tdml.DataFrame, "corr"):
    tdml.DataFrame.corr = corr

# --- patch: tdml.random.randn ---
from .patch import random as _random
if not hasattr(tdml, "random"):
    tdml.random = type("random", (), {})()
if not hasattr(tdml.random, "randn"):
    tdml.random.randn = _random.randn

# --- patch: tdml.dba.amps ---
from .patch import dba as _dba
if not hasattr(tdml, "dba"):
    tdml.dba = type("dba", (), {})()
if not hasattr(tdml.dba, "get_amps_count"):
    tdml.dba.get_amps_count = _dba.get_amps_count