"""Clock correction data handling.

This module provides tools for reading, parsing, and validating satellite
clock correction data from RINEX CLK format files.
"""

from canvod.aux.clock.parser import parse_clk_file, parse_clk_header, parse_clk_data
from canvod.aux.clock.validator import validate_clk_dataset, check_clk_data_quality
from canvod.aux.clock.reader import ClkFile

__all__ = [
    'parse_clk_file',
    'parse_clk_header', 
    'parse_clk_data',
    'validate_clk_dataset',
    'check_clk_data_quality',
    'ClkFile'
]
