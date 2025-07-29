# SPDX-FileCopyrightText: 2025-present Thōm Cummings <thom-cummings@outlook.com>
#
# SPDX-License-Identifier: MIT

"""
PySFSymbols - A library for implementing SF Symbols within Python GUI applications.
"""

from .sf_symbols import fetch_symbol, fetch_all_symbols, fetch_all_names, fetch_all

__version__ = "0.1.0"

__all__ = ["fetch_symbol", "fetch_all_symbols", "fetch_all_names", "fetch_all"]
